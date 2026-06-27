CREATE TABLE `errors` (
  `action` varchar(32) NOT NULL,
  `error` varchar(128) NOT NULL,
  `count` tinyint(3) UNSIGNED NOT NULL,
  PRIMARY KEY (`action`,`error`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `past_days` (
  `time` datetime NOT NULL,
  `embedded_wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `embedded_solar` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `coal` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ccgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ocgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `nuclear` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `oil` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `hydro` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `pumped` decimal(4,2) NOT NULL DEFAULT 0.00,
  `biomass` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `battery` decimal(4,2) NOT NULL DEFAULT 0.00,
  `other` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ifa` decimal(3,2) NOT NULL DEFAULT 0.00,
  `moyle` decimal(3,2) NOT NULL DEFAULT 0.00,
  `britned` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ewic` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nemo` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ifa2` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nsl` decimal(3,2) NOT NULL DEFAULT 0.00,
  `eleclink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `viking` decimal(3,2) NOT NULL DEFAULT 0.00,
  `greenlink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `price` decimal(7,2) NOT NULL DEFAULT 0.00,
  `emissions` smallint(5) UNSIGNED NOT NULL DEFAULT 0,
  `visits` int(10) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `past_five_minutes` (
  `time` datetime NOT NULL,
  `coal` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ccgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ocgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `nuclear` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `oil` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `hydro` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `pumped` decimal(4,2) NOT NULL DEFAULT 0.00,
  `biomass` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `battery` decimal(4,2) NOT NULL DEFAULT 0.00,
  `other` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ifa` decimal(3,2) NOT NULL DEFAULT 0.00,
  `moyle` decimal(3,2) NOT NULL DEFAULT 0.00,
  `britned` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ewic` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nemo` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ifa2` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nsl` decimal(3,2) NOT NULL DEFAULT 0.00,
  `eleclink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `viking` decimal(3,2) NOT NULL DEFAULT 0.00,
  `greenlink` decimal(3,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `past_half_hours` (
  `time` datetime NOT NULL,
  `embedded_wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `embedded_solar` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `coal` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ccgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ocgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `nuclear` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `oil` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `hydro` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `pumped` decimal(4,2) NOT NULL DEFAULT 0.00,
  `biomass` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `battery` decimal(4,2) NOT NULL DEFAULT 0.00,
  `other` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ifa` decimal(3,2) NOT NULL DEFAULT 0.00,
  `moyle` decimal(3,2) NOT NULL DEFAULT 0.00,
  `britned` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ewic` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nemo` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ifa2` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nsl` decimal(3,2) NOT NULL DEFAULT 0.00,
  `eleclink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `viking` decimal(3,2) NOT NULL DEFAULT 0.00,
  `greenlink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `price` decimal(7,2) NOT NULL DEFAULT 0.00,
  `emissions` smallint(5) UNSIGNED NOT NULL DEFAULT 0,
  `visits` int(10) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `past_weeks` (
  `time` datetime NOT NULL,
  `embedded_wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `embedded_solar` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `coal` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ccgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ocgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `nuclear` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `oil` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `hydro` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `pumped` decimal(4,2) NOT NULL DEFAULT 0.00,
  `biomass` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `battery` decimal(4,2) NOT NULL DEFAULT 0.00,
  `other` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ifa` decimal(3,2) NOT NULL DEFAULT 0.00,
  `moyle` decimal(3,2) NOT NULL DEFAULT 0.00,
  `britned` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ewic` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nemo` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ifa2` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nsl` decimal(3,2) NOT NULL DEFAULT 0.00,
  `eleclink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `viking` decimal(3,2) NOT NULL DEFAULT 0.00,
  `greenlink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `price` decimal(7,2) NOT NULL DEFAULT 0.00,
  `emissions` smallint(5) UNSIGNED NOT NULL DEFAULT 0,
  `visits` int(10) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `past_years` (
  `time` datetime NOT NULL,
  `embedded_wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `embedded_solar` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `coal` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ccgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ocgt` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `nuclear` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `oil` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `wind` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `hydro` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `pumped` decimal(4,2) NOT NULL DEFAULT 0.00,
  `biomass` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `battery` decimal(4,2) NOT NULL DEFAULT 0.00,
  `other` decimal(4,2) UNSIGNED NOT NULL DEFAULT 0.00,
  `ifa` decimal(3,2) NOT NULL DEFAULT 0.00,
  `moyle` decimal(3,2) NOT NULL DEFAULT 0.00,
  `britned` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ewic` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nemo` decimal(3,2) NOT NULL DEFAULT 0.00,
  `ifa2` decimal(3,2) NOT NULL DEFAULT 0.00,
  `nsl` decimal(3,2) NOT NULL DEFAULT 0.00,
  `eleclink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `viking` decimal(3,2) NOT NULL DEFAULT 0.00,
  `greenlink` decimal(3,2) NOT NULL DEFAULT 0.00,
  `price` decimal(7,2) NOT NULL DEFAULT 0.00,
  `emissions` smallint(5) UNSIGNED NOT NULL DEFAULT 0,
  `visits` int(10) UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `wind_records` (
  `value` decimal(4,2) UNSIGNED NOT NULL,
  `time` datetime NOT NULL,
  PRIMARY KEY (`value`),
  KEY `time` (`time`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `raw_electricity_demand` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `timestamp_utc` datetime NOT NULL,
  `electricity_demand_mw` decimal(12,3) DEFAULT NULL,
  `electricity_demand_mwh` decimal(12,3) DEFAULT NULL,
  `source_name` varchar(64) NOT NULL,
  `source_dataset` varchar(64) NOT NULL,
  `source_publish_time_utc` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `timestamp_utc` (`timestamp_utc`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `raw_electricity_forecast` LIKE `raw_electricity_demand`;

CREATE TABLE `raw_gas_demand` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `timestamp_utc` datetime NOT NULL,
  `gas_demand_original_value` decimal(16,6) DEFAULT NULL,
  `gas_demand_original_unit` varchar(16) DEFAULT NULL,
  `gas_demand_mwh_equivalent` decimal(16,6) DEFAULT NULL,
  `calorific_value_used` decimal(10,6) DEFAULT NULL,
  `conversion_method` varchar(64) DEFAULT NULL,
  `source_name` varchar(64) NOT NULL,
  `source_dataset` varchar(64) NOT NULL,
  `source_publish_time_utc` datetime DEFAULT NULL,
  `valid_for_training` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `timestamp_utc` (`timestamp_utc`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `raw_gas_forecast` LIKE `raw_gas_demand`;

CREATE TABLE `raw_weather_observed` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `region_id` varchar(64) NOT NULL,
  `target_time_utc` datetime NOT NULL,
  `temperature_2m_c` decimal(8,3) DEFAULT NULL,
  `apparent_temperature_c` decimal(8,3) DEFAULT NULL,
  `wind_speed_10m_ms` decimal(8,3) DEFAULT NULL,
  `cloud_cover_percent` decimal(8,3) DEFAULT NULL,
  `shortwave_radiation_wm2` decimal(10,3) DEFAULT NULL,
  `precipitation_mm` decimal(8,3) DEFAULT NULL,
  `relative_humidity_percent` decimal(8,3) DEFAULT NULL,
  `weather_source` varchar(64) NOT NULL,
  `weather_run_time_utc` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `target_time_utc` (`target_time_utc`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `raw_weather_forecast` LIKE `raw_weather_observed`;

CREATE TABLE `raw_calendar` (
  `timestamp_utc` datetime NOT NULL,
  `timestamp_local` datetime NOT NULL,
  `date_local` date NOT NULL,
  `hour_local` tinyint unsigned NOT NULL,
  `day_of_week` tinyint unsigned NOT NULL,
  `day_of_month` tinyint unsigned NOT NULL,
  `month` tinyint unsigned NOT NULL,
  `day_of_year` smallint unsigned NOT NULL,
  `is_weekend` tinyint(1) NOT NULL,
  `is_bank_holiday` tinyint(1) NOT NULL,
  `days_to_next_bank_holiday` smallint NOT NULL,
  `days_since_previous_bank_holiday` smallint NOT NULL,
  `is_christmas_period` tinyint(1) NOT NULL,
  `is_new_year_period` tinyint(1) NOT NULL,
  `is_dst_transition_day` tinyint(1) NOT NULL,
  PRIMARY KEY (`timestamp_utc`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `feature_hourly_actuals` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `target_time_utc` datetime NOT NULL,
  `electricity_hourly_mwh` decimal(14,4) DEFAULT NULL,
  `gas_hourly_mwh_equivalent` decimal(14,4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `target_time_utc` (`target_time_utc`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `feature_hourly_forecast_inputs` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `forecast_issue_time_utc` datetime NOT NULL,
  `target_time_utc` datetime NOT NULL,
  `horizon_hours` int NOT NULL,
  `feature_payload_json` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `issue_target_idx` (`forecast_issue_time_utc`,`target_time_utc`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `feature_training_asof` LIKE `feature_hourly_forecast_inputs`;
CREATE TABLE `feature_training_hindsight` LIKE `feature_hourly_forecast_inputs`;

CREATE TABLE `model_registry` (
  `model_id` varchar(64) NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `horizon_regime` varchar(64) NOT NULL,
  `quantile` varchar(8) NOT NULL,
  `model_version` varchar(64) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 0,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`model_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `model_training_runs` (
  `training_run_id` varchar(64) NOT NULL,
  `started_at` datetime NOT NULL,
  `completed_at` datetime DEFAULT NULL,
  `status` varchar(32) NOT NULL,
  `metadata_json` longtext,
  PRIMARY KEY (`training_run_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `model_backtest_results` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `training_run_id` varchar(64) NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `horizon_regime` varchar(64) NOT NULL,
  `season` varchar(16) NOT NULL,
  `day_type` varchar(16) NOT NULL,
  `metric` varchar(64) NOT NULL,
  `metric_value` decimal(16,6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `training_run_id` (`training_run_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `model_calibration_results` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `training_run_id` varchar(64) NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `horizon_regime` varchar(64) NOT NULL,
  `season` varchar(16) NOT NULL,
  `calibration_payload_json` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `training_run_id` (`training_run_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `forecast_runs` (
  `forecast_run_id` varchar(64) NOT NULL,
  `forecast_issue_time_utc` datetime NOT NULL,
  `status` varchar(32) NOT NULL,
  `model_status` varchar(32) NOT NULL,
  `confidence_score` tinyint unsigned NOT NULL,
  `metadata_json` longtext,
  PRIMARY KEY (`forecast_run_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `forecast_hourly_predictions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `forecast_run_id` varchar(64) NOT NULL,
  `target_time_utc` datetime NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `p05` decimal(16,6) DEFAULT NULL,
  `p10` decimal(16,6) DEFAULT NULL,
  `p25` decimal(16,6) DEFAULT NULL,
  `p50` decimal(16,6) DEFAULT NULL,
  `p75` decimal(16,6) DEFAULT NULL,
  `p90` decimal(16,6) DEFAULT NULL,
  `p95` decimal(16,6) DEFAULT NULL,
  `mean_prediction` decimal(16,6) DEFAULT NULL,
  `unit` varchar(16) NOT NULL,
  `forecast_regime` varchar(64) NOT NULL,
  `weather_mode` varchar(64) NOT NULL,
  `confidence_score` tinyint unsigned NOT NULL,
  `calibration_status` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `forecast_target_idx` (`forecast_run_id`,`target_time_utc`,`fuel_type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `forecast_daily_predictions` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `forecast_run_id` varchar(64) NOT NULL,
  `date_local` date NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `daily_total_p05` decimal(16,6) DEFAULT NULL,
  `daily_total_p50` decimal(16,6) DEFAULT NULL,
  `daily_total_p95` decimal(16,6) DEFAULT NULL,
  `daily_average_p05` decimal(16,6) DEFAULT NULL,
  `daily_average_p50` decimal(16,6) DEFAULT NULL,
  `daily_average_p95` decimal(16,6) DEFAULT NULL,
  `daily_peak_p05` decimal(16,6) DEFAULT NULL,
  `daily_peak_p50` decimal(16,6) DEFAULT NULL,
  `daily_peak_p95` decimal(16,6) DEFAULT NULL,
  `daily_peak_time_local` varchar(8) DEFAULT NULL,
  `unit` varchar(16) NOT NULL,
  `forecast_regime` varchar(64) NOT NULL,
  `confidence_score` tinyint unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `forecast_date_idx` (`forecast_run_id`,`date_local`,`fuel_type`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `forecast_explanations_hourly` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `forecast_run_id` varchar(64) NOT NULL,
  `target_time_utc` datetime NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `top_10_features_json` longtext NOT NULL,
  `top_10_feature_contributions_json` longtext NOT NULL,
  `feature_group_contributions_json` longtext NOT NULL,
  `plain_language_summary` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `forecast_explanations_daily` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `forecast_run_id` varchar(64) NOT NULL,
  `date_local` date NOT NULL,
  `fuel_type` varchar(16) NOT NULL,
  `top_10_features_json` longtext NOT NULL,
  `feature_group_contributions_json` longtext NOT NULL,
  `plain_language_summary` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
