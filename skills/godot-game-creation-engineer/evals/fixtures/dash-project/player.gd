extends CharacterBody2D

@export var speed := 180.0
@export var dash_speed := 520.0
@onready var dash_cooldown: Timer = $DashCooldown

func _physics_process(_delta: float) -> void:
	var direction := Input.get_axis("move_left", "move_right")
	velocity.x = direction * speed
	move_and_slide()

func can_dash() -> bool:
	return dash_cooldown.is_stopped()
