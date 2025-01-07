from django.db.models.signals import pre_save
from django.dispatch import receiver
from container.models import K8sCluster

@receiver(pre_save, sender=K8sCluster)
def ensure_single_true(sender, instance, **kwargs):
    if instance.k8s_cluster_is_default:
        # Ensure only one instance is active
        sender.objects.exclude(id=instance.id).update(k8s_cluster_is_default=False)