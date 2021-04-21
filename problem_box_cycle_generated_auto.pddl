(define (problem saint_reduced_auto)
	(:domain saint_reduced_auto)
	(:objects
	)
	(:init 
		(at l_task_planner)
		(value item_task_planner n0)
		(value barcode_task_planner n0)
		(value box_task_planner n0)
		(value obstacle_task_planner n0)
		(value gripper_task_planner n0)
		(value conveyor_task_planner n0)
		(value sorter_task_planner n0)
		(value robot_task_planner n0)
		(value warehouse_task_planner n0)
		(value box_detectability_task_planner n0)
		(value item_detectability_task_planner n0)
		(value readability_task_planner n0)
		(value graspability_task_planner n0)
		(value movability_task_planner n0)
		(leq n0 n0)
		(leq n0 n1)
		(leq n0 n2)
		(leq n0 n3)
		(leq n0 n4)
		(leq n0 n5)
		(leq n0 n6)
		(leq n0 n7)
		(leq n0 n8)
		(leq n1 n1)
		(leq n1 n2)
		(leq n1 n3)
		(leq n1 n4)
		(leq n1 n5)
		(leq n1 n6)
		(leq n1 n7)
		(leq n1 n8)
		(leq n2 n2)
		(leq n2 n3)
		(leq n2 n4)
		(leq n2 n5)
		(leq n2 n6)
		(leq n2 n7)
		(leq n2 n8)
		(leq n3 n3)
		(leq n3 n4)
		(leq n3 n5)
		(leq n3 n6)
		(leq n3 n7)
		(leq n3 n8)
		(leq n4 n4)
		(leq n4 n5)
		(leq n4 n6)
		(leq n4 n7)
		(leq n4 n8)
		(leq n5 n5)
		(leq n5 n6)
		(leq n5 n7)
		(leq n5 n8)
		(leq n6 n6)
		(leq n6 n7)
		(leq n6 n8)
		(leq n7 n7)
		(leq n7 n8)
		(leq n8 n8)
	)
	(:goal 
        (and
            (value item n5)
            (value gripper n1)
        )
	)
)