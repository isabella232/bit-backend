from backend import db
from backend.models import Badge, ActivityBadgePrereqs, ModuleBadgePrereqs, TopicBadgePrereqs


# Function that creates a badge_reqs depending on the object_type
def assign_badge_prereqs(badge_data, selected_object, object_type):
    for badge_info in badge_data:
        xp = badge_info["xp"]
        badge = Badge.query.get(badge_info["id"])

        # If the badge exists, then add the badge to the object
        if badge:
            target_badge = None

            if object_type == "Activity":
                target_badge = ActivityBadgePrereqs(xp=xp)
                target_badge.badge = badge
                target_badge.activity_id = selected_object.id
            elif object_type == "Module":
                target_badge = ModuleBadgePrereqs(xp=xp)
                target_badge.badge = badge
                target_badge.module_id = selected_object.id
            elif object_type == "Topic":
                target_badge = TopicBadgePrereqs(xp=xp)
                target_badge.badge = badge
                target_badge.topic_id = selected_object.id

            selected_object.badge_prereqs.append(target_badge)

    return


# Function to delete badge prereqs based on the selected object
# selected object could be an Activity, Module
def delete_badge_prereqs(selected_object):
    for badge in selected_object.badge_prereqs:
        db.session.delete(badge)
    db.session.commit()

    return