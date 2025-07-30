use crate::error::CacheResult;
use crate::eviction::{CombinedEviction, EvictionPolicy, EvictionStrategy};
use crate::memory_cache::MemoryCache;
use crate::migration::{detect_diskcache_format, DiskCacheMigrator};
use crate::serialization::{CacheEntry, OptimizedSerializer};
use crate::storage::{OptimizedStorage, StorageBackend};
use crate::utils::{current_timestamp, validate_cache_config, validate_key, CacheStats};
use parking_lot::RwLock;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::path::PathBuf;
use std::sync::Arc;

// Simplified: Only one storage backend option
// No need for enum - always use OptimizedStorage

/// Simplified cache configuration
#[derive(Debug, Clone)]
pub struct CacheConfig {
    pub directory: PathBuf,
    pub max_size: Option<u64>,
    pub max_entries: Option<u64>,
    pub eviction_strategy: EvictionStrategy,
    // All other options are now optimized defaults
}

impl Default for CacheConfig {
    fn default() -> Self {
        Self {
            directory: PathBuf::from("./cache"),
            max_size: Some(1024 * 1024 * 1024), // 1GB
            max_entries: Some(100_000),
            eviction_strategy: EvictionStrategy::LeastRecentlyStored,
        }
    }
}

/// High-performance disk cache implementation
pub struct DiskCache {
    config: CacheConfig,
    storage: Box<dyn StorageBackend>,
    eviction: Box<dyn EvictionPolicy>,
    serializer: OptimizedSerializer,
    stats: Arc<RwLock<CacheStats>>,
    last_vacuum: Arc<RwLock<u64>>,
    memory_cache: Option<MemoryCache>,
}

impl DiskCache {
    /// Check if we need to track access times for the current eviction strategy
    fn needs_access_time_tracking(&self) -> bool {
        matches!(
            self.config.eviction_strategy,
            EvictionStrategy::Lru
                | EvictionStrategy::LruTtl
                | EvictionStrategy::Lfu
                | EvictionStrategy::LfuTtl
        )
    }

    /// Create a new high-performance cache instance
    pub fn new(config: CacheConfig) -> CacheResult<Self> {
        // Validate configuration parameters
        validate_cache_config(config.max_size, config.max_entries, &config.directory)?;

        // Initialize optimized storage backend
        let storage: Box<dyn StorageBackend> = Box::new(OptimizedStorage::new(&config.directory)?);

        // Setup eviction policy
        let eviction = Box::new(CombinedEviction::new(config.eviction_strategy));

        // Initialize optimized serializer (MessagePack with LZ4)
        let serializer = OptimizedSerializer;

        // Enable memory cache for optimal performance
        let memory_cache = Some(MemoryCache::new(
            10_000,           // 10K entries
            64 * 1024 * 1024, // 64MB
        ));

        let mut cache = Self {
            config,
            storage,
            eviction,
            serializer,
            stats: Arc::new(RwLock::new(CacheStats::new())),
            last_vacuum: Arc::new(RwLock::new(current_timestamp())),
            memory_cache,
        };

        // Automatically migrate existing diskcache data for compatibility
        cache.migrate_existing_data()?;

        Ok(cache)
    }

    /// Create a cache with default configuration in the specified directory
    pub fn with_directory<P: Into<PathBuf>>(directory: P) -> CacheResult<Self> {
        let config = CacheConfig {
            directory: directory.into(),
            ..Default::default()
        };
        Self::new(config)
    }

    /// Get a value from the cache
    pub fn get(&self, key: &str) -> CacheResult<Option<Vec<u8>>> {
        validate_key(key)?;

        let should_track_access = self.needs_access_time_tracking();

        // Try memory cache first
        if let Some(ref memory_cache) = self.memory_cache {
            if let Some(entry) = memory_cache.get(key) {
                // Fast path: only update eviction policy if needed
                if should_track_access {
                    self.eviction.on_access(key, &entry);
                }

                // Update stats
                self.stats.write().hits += 1;

                // Extract data based on storage mode
                match &entry.storage {
                    crate::serialization::StorageMode::Inline(data) => {
                        return Ok(Some(data.clone()));
                    }
                    crate::serialization::StorageMode::File(filename) => {
                        let data = self.storage.read_data_file(filename)?;
                        return Ok(Some(data));
                    }
                }
            }
        }

        // Try disk storage
        match self.storage.get(key)? {
            Some(entry) => {
                // Fast path: only update eviction policy if needed
                if should_track_access {
                    self.eviction.on_access(key, &entry);
                }

                // Store in memory cache for future access (without modifying the entry)
                if let Some(ref memory_cache) = self.memory_cache {
                    memory_cache.put(key.to_string(), entry.clone());
                }

                // Update stats
                self.stats.write().hits += 1;

                // Extract data based on storage mode
                match &entry.storage {
                    crate::serialization::StorageMode::Inline(data) => Ok(Some(data.clone())),
                    crate::serialization::StorageMode::File(filename) => {
                        let data = self.storage.read_data_file(filename)?;
                        Ok(Some(data))
                    }
                }
            }
            None => {
                self.stats.write().misses += 1;
                Ok(None)
            }
        }
    }

    /// Set a value in the cache
    pub fn set(
        &self,
        key: &str,
        value: &[u8],
        expire_time: Option<u64>,
        tags: Vec<String>,
    ) -> CacheResult<()> {
        validate_key(key)?;

        // Enforce cache size and entry limits
        self.enforce_cache_limits()?;

        // Always use inline storage for simplicity (OptimizedStorage handles the optimization)
        let entry = CacheEntry::new_inline(key.to_string(), value.to_vec(), tags, expire_time);

        // Store the entry metadata
        self.storage.set(key, entry.clone())?;
        self.eviction.on_insert(key, &entry);

        // Store in memory cache
        if let Some(ref memory_cache) = self.memory_cache {
            memory_cache.put(key.to_string(), entry.clone());
        }

        // Update stats
        let mut stats = self.stats.write();
        stats.sets += 1;
        stats.total_size += entry.size;
        stats.entry_count += 1;

        Ok(())
    }

    /// Delete a value from the cache
    pub fn delete(&self, key: &str) -> CacheResult<bool> {
        validate_key(key)?;

        let existed = self.storage.delete(key)?;
        if existed {
            self.eviction.on_remove(key);

            // Remove from memory cache
            if let Some(ref memory_cache) = self.memory_cache {
                memory_cache.remove(key);
            }

            let mut stats = self.stats.write();
            stats.deletes += 1;
            stats.entry_count = stats.entry_count.saturating_sub(1);
        }

        Ok(existed)
    }

    /// Check if a key exists in the cache
    pub fn exists(&self, key: &str) -> CacheResult<bool> {
        validate_key(key)?;
        self.storage.exists(key)
    }

    /// Get all keys in the cache
    pub fn keys(&self) -> CacheResult<Vec<String>> {
        self.storage.keys()
    }

    /// Clear all entries from the cache
    pub fn clear(&self) -> CacheResult<()> {
        self.storage.clear()?;
        self.eviction.clear();

        // Clear memory cache
        if let Some(ref memory_cache) = self.memory_cache {
            memory_cache.clear();
        }

        let mut stats = self.stats.write();
        *stats = CacheStats::new();

        Ok(())
    }

    /// Get cache statistics
    pub fn stats(&self) -> CacheStats {
        self.stats.read().clone()
    }

    /// Get current cache size in bytes (estimated)
    pub fn size(&self) -> CacheResult<u64> {
        // Estimate size from stats
        Ok(self.stats.read().total_size)
    }

    /// Manually trigger vacuum operation
    pub fn vacuum(&self) -> CacheResult<()> {
        self.storage.vacuum()?;
        *self.last_vacuum.write() = current_timestamp();
        Ok(())
    }

    /// Check cache limits and evict entries if necessary
    fn enforce_cache_limits(&self) -> CacheResult<()> {
        let current_size = self.size()?;
        let current_entries = self.keys()?.len() as u64;

        let mut evict_count = 0;

        // Check size limit
        if let Some(max_size) = self.config.max_size {
            if current_size > max_size {
                // Evict 10% of entries or enough to get under limit
                evict_count = std::cmp::max(evict_count, (current_entries / 10).max(1));
            }
        }

        // Check entry count limit
        if let Some(max_entries) = self.config.max_entries {
            if current_entries > max_entries {
                evict_count = std::cmp::max(
                    evict_count,
                    current_entries - max_entries + (max_entries / 10),
                );
            }
        }

        // Perform eviction
        if evict_count > 0 {
            let victims = self.eviction.select_victims(evict_count as usize);
            for key in victims {
                self.storage.delete(&key)?;
                self.eviction.on_remove(&key);
                self.stats.write().evictions += 1;
            }
        }

        // Auto vacuum every hour
        let last_vacuum = *self.last_vacuum.read();
        let now = current_timestamp();
        if now - last_vacuum > 3600 {
            // 1 hour
            self.vacuum()?;
        }

        Ok(())
    }

    /// Automatically migrate existing diskcache data if detected
    fn migrate_existing_data(&mut self) -> CacheResult<()> {
        if detect_diskcache_format(&self.config.directory) {
            tracing::info!("Detected python-diskcache data, starting auto-migration...");

            // Create a backup first
            let backup_dir = self.config.directory.join("diskcache_backup");
            if !backup_dir.exists() {
                let cache_db = self.config.directory.join("cache.db");
                let backup_db = backup_dir.join("cache.db");
                std::fs::create_dir_all(&backup_dir)?;
                std::fs::copy(&cache_db, &backup_db)?;
                tracing::info!("Created backup at: {:?}", backup_dir);
            }

            // Perform migration using OptimizedStorage
            let mut migrator = DiskCacheMigrator::new(
                self.config.directory.clone(),
                Box::new(OptimizedStorage::new(&self.config.directory)?),
            );

            match migrator.migrate() {
                Ok(stats) => {
                    tracing::info!("Migration completed: {:?}", stats);
                    if stats.success {
                        // Rename the original database to avoid future migrations
                        let cache_db = self.config.directory.join("cache.db");
                        let migrated_db = self.config.directory.join("cache.db.migrated");
                        if cache_db.exists() && !migrated_db.exists() {
                            std::fs::rename(&cache_db, &migrated_db)?;
                        }
                    }
                }
                Err(e) => {
                    tracing::warn!("Migration failed: {}", e);
                    // Continue without migration
                }
            }
        }

        Ok(())
    }

    /// Get memory cache statistics
    pub fn memory_stats(&self) -> Option<crate::memory_cache::MemoryCacheStats> {
        self.memory_cache.as_ref().map(|mc| mc.stats())
    }

    /// Manually migrate from python-diskcache
    pub fn migrate_from_diskcache(&mut self) -> CacheResult<crate::migration::MigrationStats> {
        let mut migrator = DiskCacheMigrator::new(
            self.config.directory.clone(),
            Box::new(OptimizedStorage::new(&self.config.directory)?),
        );

        migrator.migrate()
    }
}

/// Python wrapper for the Cache
#[pyclass]
pub struct PyCache {
    cache: DiskCache,
}

#[pymethods]
impl PyCache {
    #[new]
    #[pyo3(signature = (directory, max_size=None, max_entries=None))]
    fn new(directory: String, max_size: Option<u64>, max_entries: Option<u64>) -> PyResult<Self> {
        let mut config = CacheConfig {
            directory: PathBuf::from(directory),
            ..Default::default()
        };
        config.max_size = max_size;
        config.max_entries = max_entries;

        let cache = DiskCache::new(config)?;
        Ok(Self { cache })
    }

    fn get(&self, key: &str) -> PyResult<Option<Vec<u8>>> {
        Ok(self.cache.get(key)?)
    }

    #[pyo3(signature = (key, value, expire_time=None, tags=None))]
    fn set(
        &self,
        key: &str,
        value: PyObject,
        expire_time: Option<u64>,
        tags: Option<Vec<String>>,
    ) -> PyResult<()> {
        let tags = tags.unwrap_or_default();
        // Convert PyObject to bytes for internal storage
        let value_bytes = Python::with_gil(|py| {
            let bytes = value.extract::<Vec<u8>>(py)?;
            Ok::<Vec<u8>, PyErr>(bytes)
        })?;
        Ok(self.cache.set(key, &value_bytes, expire_time, tags)?)
    }

    /// Set multiple values in the cache (batch operation for better performance)
    #[pyo3(signature = (items, expire_time=None, tags=None))]
    fn set_many(
        &self,
        items: Vec<(String, Vec<u8>)>,
        expire_time: Option<u64>,
        tags: Option<Vec<String>>,
    ) -> PyResult<()> {
        let tags = tags.unwrap_or_default();

        // For now, use individual operations but optimize the loop
        for (key, value) in items {
            self.cache.set(&key, &value, expire_time, tags.clone())?;
        }

        Ok(())
    }

    fn delete(&self, key: &str) -> PyResult<bool> {
        Ok(self.cache.delete(key)?)
    }

    fn exists(&self, key: &str) -> PyResult<bool> {
        Ok(self.cache.exists(key)?)
    }

    fn keys(&self) -> PyResult<Vec<String>> {
        Ok(self.cache.keys()?)
    }

    fn clear(&self) -> PyResult<()> {
        Ok(self.cache.clear()?)
    }

    fn size(&self) -> PyResult<u64> {
        Ok(self.cache.size()?)
    }

    fn vacuum(&self) -> PyResult<()> {
        Ok(self.cache.vacuum()?)
    }

    fn stats(&self) -> PyResult<HashMap<String, u64>> {
        let stats = self.cache.stats();
        let mut result = HashMap::new();
        result.insert("hits".to_string(), stats.hits);
        result.insert("misses".to_string(), stats.misses);
        result.insert("sets".to_string(), stats.sets);
        result.insert("deletes".to_string(), stats.deletes);
        result.insert("evictions".to_string(), stats.evictions);
        result.insert("errors".to_string(), stats.errors);
        result.insert("total_size".to_string(), stats.total_size);
        result.insert("entry_count".to_string(), stats.entry_count);
        Ok(result)
    }

    fn hit_rate(&self) -> PyResult<f64> {
        Ok(self.cache.stats().hit_rate())
    }
}

/// Drop-in replacement for diskcache.Cache
#[pyclass(name = "Cache")]
pub struct RustCache {
    cache: DiskCache,
}

#[pymethods]
impl RustCache {
    #[new]
    #[pyo3(signature = (directory, **kwargs))]
    fn new(directory: String, kwargs: Option<&Bound<'_, pyo3::types::PyDict>>) -> PyResult<Self> {
        let mut config = CacheConfig {
            directory: PathBuf::from(directory),
            ..Default::default()
        };

        // Parse kwargs for compatibility with diskcache.Cache
        if let Some(kwargs) = kwargs {
            if let Ok(Some(size_limit)) = kwargs.get_item("size_limit") {
                config.max_size = size_limit.extract::<Option<u64>>()?;
            }

            if let Ok(Some(count_limit)) = kwargs.get_item("count_limit") {
                config.max_entries = count_limit.extract::<Option<u64>>()?;
            }
        }

        let cache = DiskCache::new(config)?;
        Ok(Self { cache })
    }

    fn get(
        &self,
        key: &str,
        default: Option<&Bound<'_, pyo3::PyAny>>,
    ) -> PyResult<Option<Vec<u8>>> {
        match self.cache.get(key)? {
            Some(value) => Ok(Some(value)),
            None => {
                if let Some(default) = default {
                    // Convert default to bytes if needed
                    if let Ok(bytes) = default.extract::<Vec<u8>>() {
                        Ok(Some(bytes))
                    } else {
                        Ok(None)
                    }
                } else {
                    Ok(None)
                }
            }
        }
    }

    #[pyo3(signature = (key, value, expire=None, read=None, tag=None, retry=None))]
    fn set(
        &self,
        key: &str,
        value: PyObject,
        expire: Option<u64>,
        read: Option<bool>,
        tag: Option<String>,
        retry: Option<bool>,
    ) -> PyResult<bool> {
        let _ = read; // Unused parameter for compatibility
        let _ = retry; // Unused parameter for compatibility

        let tags = if let Some(tag) = tag {
            vec![tag]
        } else {
            vec![]
        };

        // Convert PyObject to bytes for internal storage
        let value_bytes = Python::with_gil(|py| {
            let bytes = value.extract::<Vec<u8>>(py)?;
            Ok::<Vec<u8>, PyErr>(bytes)
        })?;
        self.cache.set(key, &value_bytes, expire, tags)?;
        Ok(true)
    }

    fn delete(&self, key: &str) -> PyResult<bool> {
        Ok(self.cache.delete(key)?)
    }

    // Implement __contains__ for 'key in cache' syntax
    fn __contains__(&self, key: &str) -> PyResult<bool> {
        Ok(self.cache.exists(key)?)
    }

    // Implement iterkeys() for compatibility
    fn iterkeys(&self) -> PyResult<Vec<String>> {
        Ok(self.cache.keys()?)
    }

    fn clear(&self) -> PyResult<()> {
        Ok(self.cache.clear()?)
    }

    fn stats(&self) -> PyResult<(u64, u64)> {
        let stats = self.cache.stats();
        // Return (hits, misses) tuple like diskcache
        Ok((stats.hits, stats.misses))
    }

    fn volume(&self) -> PyResult<u64> {
        Ok(self.cache.size()?)
    }

    fn __len__(&self) -> PyResult<usize> {
        let stats = self.cache.stats();
        Ok(stats.entry_count as usize)
    }
}

/// Drop-in replacement for diskcache.FanoutCache
#[pyclass(name = "FanoutCache")]
pub struct RustFanoutCache {
    caches: Vec<RustCache>,
    shards: usize,
}

#[pymethods]
impl RustFanoutCache {
    #[new]
    #[pyo3(signature = (directory, shards=Some(8), **kwargs))]
    fn new(
        directory: String,
        shards: Option<usize>,
        kwargs: Option<&Bound<'_, pyo3::types::PyDict>>,
    ) -> PyResult<Self> {
        let shards = shards.unwrap_or(8);
        let mut caches = Vec::with_capacity(shards);

        for i in 0..shards {
            let shard_dir = format!("{}/shard_{:03}", directory, i);
            let cache = RustCache::new(shard_dir, kwargs)?;
            caches.push(cache);
        }

        Ok(Self { caches, shards })
    }

    fn get(
        &self,
        key: &str,
        default: Option<&Bound<'_, pyo3::PyAny>>,
    ) -> PyResult<Option<Vec<u8>>> {
        let shard = self.get_shard(key);
        self.caches[shard].get(key, default)
    }

    #[pyo3(signature = (key, value, expire=None, read=None, tag=None, retry=None))]
    fn set(
        &self,
        key: &str,
        value: PyObject,
        expire: Option<u64>,
        read: Option<bool>,
        tag: Option<String>,
        retry: Option<bool>,
    ) -> PyResult<bool> {
        let shard = self.get_shard(key);
        self.caches[shard].set(key, value, expire, read, tag, retry)
    }

    fn delete(&self, key: &str) -> PyResult<bool> {
        let shard = self.get_shard(key);
        self.caches[shard].delete(key)
    }

    fn __contains__(&self, key: &str) -> PyResult<bool> {
        let shard = self.get_shard(key);
        self.caches[shard].__contains__(key)
    }

    fn iterkeys(&self) -> PyResult<Vec<String>> {
        let mut all_keys = Vec::new();
        for cache in &self.caches {
            let keys = cache.iterkeys()?;
            all_keys.extend(keys);
        }
        Ok(all_keys)
    }

    fn clear(&self) -> PyResult<()> {
        for cache in &self.caches {
            cache.clear()?;
        }
        Ok(())
    }

    fn stats(&self) -> PyResult<(u64, u64)> {
        let mut total_hits = 0;
        let mut total_misses = 0;

        for cache in &self.caches {
            let (hits, misses) = cache.stats()?;
            total_hits += hits;
            total_misses += misses;
        }

        Ok((total_hits, total_misses))
    }

    fn volume(&self) -> PyResult<u64> {
        let mut total_volume = 0;
        for cache in &self.caches {
            total_volume += cache.volume()?;
        }
        Ok(total_volume)
    }

    fn __len__(&self) -> PyResult<usize> {
        let mut total_len = 0;
        for cache in &self.caches {
            total_len += cache.__len__()?;
        }
        Ok(total_len)
    }
}

impl RustFanoutCache {
    fn get_shard(&self, key: &str) -> usize {
        use std::collections::hash_map::DefaultHasher;

        let mut hasher = DefaultHasher::new();
        key.hash(&mut hasher);
        (hasher.finish() as usize) % self.shards
    }
}
