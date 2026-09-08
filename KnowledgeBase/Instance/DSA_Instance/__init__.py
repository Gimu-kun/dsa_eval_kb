from .bloom_levels import bloom_level_instances
from .chapters import chapter_overview_instance, chapter_searching_and_sorting_instance, chapter_linklist_instance
from .clos import clo1, clo2, clo3, clo4, clo5

dsa_instances = [
    chapter_overview_instance, chapter_searching_and_sorting_instance, chapter_linklist_instance,
    clo1, clo2, clo3, clo4, clo5
]
dsa_instances.extend(bloom_level_instances)