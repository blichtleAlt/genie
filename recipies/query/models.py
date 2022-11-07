from django.db import models

class Ingredient(models.Model):
    name = models.CharField(
            unique=True,
            primary_key=True,
            max_length=100,
    )
    json = models.JSONField()

    def __str__(self) -> str:
        return '{} with {}'.format(self.name, self.json)

class Recipe(models.Model):
    id = models.CharField(
            unique=True,
            primary_key=True,
            max_length=36,
    )
    json = models.JSONField()

    def __str__(self) -> str:
        return '{} with {}'.format(self.id, self.json)
