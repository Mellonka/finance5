from shared.storage.advisory_lock import with_advisory_lock


def get_user_id_from_category(kwargs) -> str:
    if kwargs.get('category') is None:
        raise ValueError('Category not provided')

    return kwargs['category'].user_id


with_lock_all_user_categories = with_advisory_lock(
    'lock_all_user_categories',
    get_lock_name_suffix=get_user_id_from_category,
)
