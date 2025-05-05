provider "google" {
    project = var.project_id
    credentials = file(var.service_account)
    region = var.region
}

resource "google_storage_bucket" "gc_bucket" {

    name = var.bucket_name
    project = var.project_id
    location = var.region
}

resource "google_bigquery_dataset" "gcp_bigquery_raw" {

    dataset_id = var.bigquery_name_1
    project = var.project_id
    location = var.region
}

resource "google_bigquery_dataset" "gcp_bigquery_clean" {

    dataset_id = var.bigquery_name_2
    project = var.project_id
    location = var.region
}