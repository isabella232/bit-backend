from backend import ma
from backend.checkpoint_progresses.schemas import CheckpointProgressSchema
from marshmallow import fields


# This schema is used to display the current card's hints data
class ActivityProgressCardHints(ma.ModelSchema):
    hints_locked = fields.Nested("HintSchema", only=("id", "contentful_id", "name"), many=True)
    hints_unlocked = fields.Nested("HintSchema", only=("id", "contentful_id", "name"), many=True)

    class Meta:
        # Fields to show when sending data
        fields = ("hints_locked", "hints_unlocked")
        ordered = True


# This schema is used to display activity progress' checkpoints for the teacher to grade
class ActivityProgressGradingSchema(ma.ModelSchema):
    student = fields.Nested("StudentSchema", only=("name",))
    activity = fields.Nested("ActivitySchema", only=("name",))
    checkpoints = fields.Nested("CheckpointProgressSchema",
                                only=("is_completed", "image_to_receive", "video_to_receive", "checkpoint"), many=True)

    class Meta:
        # Fields to show when sending data
        fields = ("student", "activity", "checkpoints")
        ordered = True


# This schema is used to display ActivityProgress data
class ActivityProgressSchema(ma.ModelSchema):
    last_card_completed = fields.Int(required=True)
    cards_locked = fields.Nested("CardSchema", only=("id", "contentful_id", "name", "order"), many=True)
    cards_unlocked = fields.Nested("CardSchema", only=("id", "contentful_id", "name", "order"), many=True)
    checkpoints = fields.Nested(CheckpointProgressSchema, only=("checkpoint_id", "contentful_id", "is_completed"),
                                many=True)

    class Meta:
        # Fields to show when sending data
        fields = (
            "last_card_completed", "cards_locked", "cards_unlocked", "checkpoints")
        ordered = True


class ActivityProgressVideo(ma.ModelSchema):
    video = fields.Str(required=True)

    class Meta:
        # Fields to show when sending data
        fields = ("video",)


activity_progress_card_hints = ActivityProgressCardHints()
activity_progress_schema = ActivityProgressSchema()
activity_progress_video = ActivityProgressVideo()
activity_progress_grading_schema = ActivityProgressGradingSchema(many=True)
