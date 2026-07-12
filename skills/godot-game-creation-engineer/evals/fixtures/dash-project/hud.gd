extends CanvasLayer

func set_dash_cooldown(remaining: float, total: float) -> void:
	%DashCooldown.value = 1.0 - (remaining / total)
