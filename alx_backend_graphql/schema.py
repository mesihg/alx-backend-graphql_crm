import graphene
class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, root, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=Query)