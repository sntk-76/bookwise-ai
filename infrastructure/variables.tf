variable project_id {
  default     = "bookwise-ai-458509"
  description = "The project id"
}

variable service_account {
  default     = "/home/sinatavakoli284/bookwise-ai/authentication/bookwise-ai-458509-014ab71d8d71.json"
  description = "The service account to communicate with gcp"
}

variable region {
  default     = "europe-west8"
  description = "The region for the selected service"
}

variable bucket_name {
  default     = "bookwise-ai-458509-bucket"
  description = "The name of the bucket in the gcp service"
}

variable bigquery_name_1 {
  default     = "raw_data"
  description = "The bigquery for the raw data in the gcp service"
}

variable bigquery_name_2 {
  default     = "clean_data"
  description = "The bigquery for the clean data in the gcp service"
}



