from django.contrib import admin

from .models import Game, Round


class RoundInline(admin.TabularInline):
    model = Round
    extra = 0
    fields = ('round_number', 'player1_choice', 'player2_choice', 'winner', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('round_number',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'player1_name',
        'player2_name',
        'player1_score',
        'player2_score',
        'ties',
        'status',
        'winner',
        'created_at',
        'completed_at',
    )
    list_filter = ('status', 'winner')
    search_fields = ('player1_name', 'player2_name')
    readonly_fields = ('created_at', 'completed_at')
    inlines = (RoundInline,)


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'game',
        'round_number',
        'player1_choice',
        'player2_choice',
        'winner',
        'created_at',
    )
    list_filter = ('winner', 'player1_choice', 'player2_choice')
    search_fields = ('game__player1_name', 'game__player2_name')
    readonly_fields = ('created_at',)
