from django.db import models

# Create your models here.

class K8sCluster(models.Model):
    k8s_cluster_name = models.CharField("k8s_cluster_name", max_length=255, help_text="k8s_cluster_name", blank=True)
    k8s_clustet_desc = models.CharField("k8s_clustet_desc", max_length=255, help_text="k8s_clustet_desc", blank=True)
    k8s_cluster_config = models.TextField("k8s_cluster_config", help_text="k8s_cluster_config", blank=True)
    k8s_exclude_namespace = models.CharField("k8s_exclude_namespace", max_length=255, help_text="k8s_exclude_namespace", blank=True)
    k8s_cluster_is_default = models.BooleanField("k8s_cluster_is_default", help_text="k8s_cluster_is_default", default=False, blank=True)
    k8s_default_namespace = models.CharField("k8s_default_namespace", max_length=255, help_text="k8s_default_namespace", blank=True, default="default")

    class Meta:
        ordering = ["id"]
        db_table = "container_k8s_cluster"