from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from education.models import Company, Course, Employee, Group, Specification

@receiver([post_save, post_delete], sender=Employee)
def invalidate_employee_cache(sender, instance, **kwargs):
  cache.delete_pattern('*employee_list*')

@receiver([post_save, post_delete], sender=Course)
def invalidate_course_cache(sender, instance, **kwargs):
  cache.delete_pattern('*course_list*')

@receiver([post_save, post_delete], sender=Company)
def invalidate_company_cache(sender, instance, **kwargs):
  cache.delete_pattern('*company_list*')

@receiver([post_save, post_delete], sender=Specification)
def invalidate_specification_cache(sender, instance, **kwargs):
  cache.delete_pattern('*specification_list*')

@receiver([post_save, post_delete], sender=Group)
def invalidate_group_cache(sender, instance, **kwargs):
  cache.delete_pattern('*group_list*')