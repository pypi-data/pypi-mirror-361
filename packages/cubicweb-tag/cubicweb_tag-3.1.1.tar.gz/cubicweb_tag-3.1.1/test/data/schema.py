from yams.buildobjs import RelationDefinition


class tags(RelationDefinition):
    subject = "Tag"
    object = ("BlogEntry", "CWUser")
