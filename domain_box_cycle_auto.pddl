; mdp
(define (domain saint_reduced_auto)
	(:types int  loc  bool  num)
	(:constants
		goal_condition - bool
		item_task_planner - int
		barcode_task_planner - int
		box_task_planner - int
		obstacle_task_planner - int
		gripper_task_planner - int
		conveyor_task_planner - int
		sorter_task_planner - int
		robot_task_planner - int
		warehouse_task_planner - int
		box_detectability_task_planner - int
		item_detectability_task_planner - int
		readability_task_planner - int
		graspability_task_planner - int
		movability_task_planner - int
		l_task_planner - loc
		n0 n1 n2 n3 n4 n5 n6 n7 n8 - num
	)
	(:predicates
		(fulfiled ?x - bool)
		(at ?l - loc)
		(value ?v - int ?n - num)
		(leq ?n1 ?n2 - num)
	)
	(:functions
	)
	(:action adapt_find_box_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value obstacle_task_planner n0)

							(and 
							(value box_detectability_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n1)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n1)
					(not (value box_detectability_task_planner ?vbox_detectability_task_planner))
					(value box_detectability_task_planner n0)
				)
	)

	(:action adapt_grasp_parameters
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value item_task_planner n1)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value box_task_planner n4)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value graspability_task_planner n1)

							(value barcode_task_planner n2)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value graspability_task_planner ?vgraspability_task_planner))
					(value graspability_task_planner n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value conveyor_task_planner n2)

							(and 
							(value warehouse_task_planner n3)

							(and 
							(value item_detectability_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n1)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n2)
					(not (value item_detectability_task_planner ?vitem_detectability_task_planner))
					(value item_detectability_task_planner n0)
					(not (value readability_task_planner ?vreadability_task_planner))
					(value readability_task_planner n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value conveyor_task_planner n2)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value item_detectability_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n1)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n2)
					(not (value item_detectability_task_planner ?vitem_detectability_task_planner))
					(value item_detectability_task_planner n0)
					(not (value readability_task_planner ?vreadability_task_planner))
					(value readability_task_planner n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value conveyor_task_planner n2)

							(and 
							(value warehouse_task_planner n3)

							(and 
							(value readability_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n1)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n2)
					(not (value item_detectability_task_planner ?vitem_detectability_task_planner))
					(value item_detectability_task_planner n0)
					(not (value readability_task_planner ?vreadability_task_planner))
					(value readability_task_planner n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value conveyor_task_planner n2)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value readability_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n1)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n2)
					(not (value item_detectability_task_planner ?vitem_detectability_task_planner))
					(value item_detectability_task_planner n0)
					(not (value readability_task_planner ?vreadability_task_planner))
					(value readability_task_planner n0)
				)
	)

	(:action blind_grasp
		:parameters (
		 ?vitem_task_planner - num
		 ?vreadability_task_planner - num
		 ?vgraspability_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value graspability_task_planner ?vgraspability_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(value readability_task_planner ?vreadability_task_planner)
			(and 
							(value gripper_task_planner n1)

							(and 
							(value item_detectability_task_planner n2)

							(and 
							(value box_task_planner n4)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value robot_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value conveyor_task_planner n2)

			)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n2)
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n3)
					(not (value item_detectability_task_planner ?vitem_detectability_task_planner))
					(value item_detectability_task_planner n0)
					(not (value readability_task_planner ?vreadability_task_planner))
					(value readability_task_planner n0)
					(not (value graspability_task_planner ?vgraspability_task_planner))
					(value graspability_task_planner n0)
				)
	)

	(:action box_arrived
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n1)

							(value conveyor_task_planner n1)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n2)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n2)
				)
	)

	(:action check_barcode
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value barcode_task_planner n1)

							(value warehouse_task_planner n3)

			)

		)
		:effect
			 1 
				(and 
					(not (value barcode_task_planner ?vbarcode_task_planner))
					(value barcode_task_planner n2)
					(not (value warehouse_task_planner ?vwarehouse_task_planner))
					(value warehouse_task_planner n4)
				)
	)

	(:action check_empty
		:parameters (
		 ?vitem_task_planner - num
		 ?vbarcode_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value barcode_task_planner ?vbarcode_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(and 
							(value box_task_planner n4)

							(and 
							(value robot_task_planner n6)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value warehouse_task_planner n6)

							(value gripper_task_planner n1)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value barcode_task_planner ?vbarcode_task_planner))
					(value barcode_task_planner n0)
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n5)
					(not (value warehouse_task_planner ?vwarehouse_task_planner))
					(value warehouse_task_planner n1)
				)
	)

	(:action check_gripper_free
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value item_task_planner n0)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value robot_task_planner n5)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n0)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n5)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n1)
					(not (value warehouse_task_planner ?vwarehouse_task_planner))
					(value warehouse_task_planner n0)
				)
	)

	(:action check_gripper_occupied
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value movability_task_planner n0)

							(and 
							(value gripper_task_planner n2)

							(value item_task_planner n3)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n2)
				)
	)

	(:action detect_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n0)

							(and 
							(value box_detectability_task_planner n0)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value robot_task_planner n1)

							(and 
							(value warehouse_task_planner n2)

							(value gripper_task_planner n1)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n3)
				)
	)

	(:action detect_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n2)

							(and 
							(value box_detectability_task_planner n0)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value robot_task_planner n1)

							(and 
							(value warehouse_task_planner n2)

							(value gripper_task_planner n1)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n3)
				)
	)

	(:action detect_item
		:parameters (
		 ?vitem_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(and 
							(value gripper_task_planner n1)

							(and 
							(value warehouse_task_planner n3)

							(and 
							(not (value item_task_planner n1))

							(and 
							(value item_detectability_task_planner n0)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value robot_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value box_task_planner n4)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n1)
				)
	)

	(:action detect_item
		:parameters (
		 ?vitem_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(and 
							(value gripper_task_planner n1)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(not (value item_task_planner n1))

							(and 
							(value item_detectability_task_planner n0)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value robot_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value box_task_planner n4)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n1)
				)
	)

	(:action detect_obstacle
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value obstacle_task_planner n1)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value robot_task_planner n8)

							(value gripper_task_planner n1)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value obstacle_task_planner ?vobstacle_task_planner))
					(value obstacle_task_planner n0)
				)
	)

	(:action dispose_item
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value item_task_planner n0)

							(value gripper_task_planner n2)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n1)
				)
	)

	(:action drop_item_in_box
		:parameters (
		 ?vitem_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(and 
							(not (value item_task_planner n0))

							(and 
							(value robot_task_planner n2)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value gripper_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value box_task_planner n4)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n1)
				)
	)

	(:action drop_item_in_box
		:parameters (
		 ?vitem_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(and 
							(not (value item_task_planner n0))

							(and 
							(value robot_task_planner n3)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value gripper_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value box_task_planner n4)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n1)
				)
	)

	(:action explore_gripper
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value gripper_task_planner n0)

							(value movability_task_planner n0)

			)

		)
		:effect
			 1 
				(and 
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n1)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n0)

							(and 
							(value warehouse_task_planner n2)

							(and 
							(value gripper_task_planner n1)

							(and 
							(value robot_task_planner n1)

							(and 
							(value box_detectability_task_planner n2)

							(value conveyor_task_planner n2)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n3)
					(not (value box_detectability_task_planner ?vbox_detectability_task_planner))
					(value box_detectability_task_planner n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n2)

							(and 
							(value warehouse_task_planner n2)

							(and 
							(value gripper_task_planner n1)

							(and 
							(value robot_task_planner n1)

							(and 
							(value box_detectability_task_planner n2)

							(value conveyor_task_planner n2)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n3)
					(not (value box_detectability_task_planner ?vbox_detectability_task_planner))
					(value box_detectability_task_planner n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n0)

							(and 
							(value warehouse_task_planner n2)

							(and 
							(value gripper_task_planner n1)

							(and 
							(value robot_task_planner n7)

							(and 
							(value box_detectability_task_planner n2)

							(value conveyor_task_planner n2)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n3)
					(not (value box_detectability_task_planner ?vbox_detectability_task_planner))
					(value box_detectability_task_planner n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n2)

							(and 
							(value warehouse_task_planner n2)

							(and 
							(value gripper_task_planner n1)

							(and 
							(value robot_task_planner n7)

							(and 
							(value box_detectability_task_planner n2)

							(value conveyor_task_planner n2)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n3)
					(not (value box_detectability_task_planner ?vbox_detectability_task_planner))
					(value box_detectability_task_planner n0)
				)
	)

	(:action facility_explore_box
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(value box_task_planner n0)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n2)
				)
	)

	(:action facility_explore_conveyor
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner n0)

		)
		:effect
			 1 
				(and 
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n2)
				)
	)

	(:action facility_explore_sorter
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(value sorter_task_planner n0)

		)
		:effect
			 1 
				(and 
					(not (value sorter_task_planner ?vsorter_task_planner))
					(value sorter_task_planner n1)
				)
	)

	(:action facility_reset_motion
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(value movability_task_planner n1)

		)
		:effect
			 1 
				(and 
					(not (value movability_task_planner ?vmovability_task_planner))
					(value movability_task_planner n0)
				)
	)

	(:action flip_item
		:parameters (
		 ?vitem_task_planner - num
		 ?vitem_detectability_task_planner - num
		 ?vreadability_task_planner - num
		 ?vgraspability_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value graspability_task_planner ?vgraspability_task_planner)
			(value readability_task_planner ?vreadability_task_planner)
			(value item_task_planner ?vitem_task_planner)
			(value item_detectability_task_planner ?vitem_detectability_task_planner)
			(and 
							(value box_task_planner n4)

							(and 
							(value robot_task_planner n2)

							(and 
							(value gripper_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value conveyor_task_planner n2)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n0)
					(not (value item_detectability_task_planner ?vitem_detectability_task_planner))
					(value item_detectability_task_planner n0)
					(not (value readability_task_planner ?vreadability_task_planner))
					(value readability_task_planner n0)
					(not (value graspability_task_planner ?vgraspability_task_planner))
					(value graspability_task_planner n0)
				)
	)

	(:action get_box_info
		:parameters (
		 ?vwarehouse_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value warehouse_task_planner ?vwarehouse_task_planner)
			(value box_task_planner n3)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n4)
					(not (value warehouse_task_planner ?vwarehouse_task_planner))
					(value warehouse_task_planner n3)
				)
	)

	(:action get_decommission_info
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value warehouse_task_planner n5)

							(and 
							(value box_task_planner n4)

							(value gripper_task_planner n1)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value warehouse_task_planner ?vwarehouse_task_planner))
					(value warehouse_task_planner n6)
				)
	)

	(:action grasp
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value gripper_task_planner n1)

							(and 
							(value robot_task_planner n2)

							(and 
							(value item_task_planner n1)

							(and 
							(value graspability_task_planner n0)

							(and 
							(value box_task_planner n4)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value barcode_task_planner n2)

			)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n2)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n2)
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n3)
				)
	)

	(:action move_home
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value movability_task_planner n0)

							(and 
							(value obstacle_task_planner n0)

							(value conveyor_task_planner n2)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n7)
				)
	)

	(:action move_to_check_empty_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value box_task_planner n4)

							(and 
							(not (value robot_task_planner n6))

							(and 
							(value gripper_task_planner n1)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value obstacle_task_planner n0)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n6)
				)
	)

	(:action move_to_find_box_pose
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value obstacle_task_planner n0)

							(and 
							(value robot_task_planner n7)

							(and 
							(value movability_task_planner n0)

							(value gripper_task_planner n1)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n1)
				)
	)

	(:action move_to_find_obstacle_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value obstacle_task_planner n1)

							(and 
							(not (value robot_task_planner n8))

							(and 
							(value movability_task_planner n0)

							(value conveyor_task_planner n2)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n8)
				)
	)

	(:action move_to_inspect_box_pose
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value box_task_planner n4)

							(and 
							(not (value robot_task_planner n2))

							(and 
							(value gripper_task_planner n1)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value obstacle_task_planner n0)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n2)
				)
	)

	(:action move_to_place_pose
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value item_task_planner n2)

							(and 
							(value robot_task_planner n4)

							(and 
							(value sorter_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value obstacle_task_planner n0)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n5)
				)
	)

	(:action place
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value gripper_task_planner n2)

							(and 
							(value robot_task_planner n5)

							(and 
							(value item_task_planner n2)

							(and 
							(value warehouse_task_planner n4)

							(and 
							(value sorter_task_planner n1)

							(and 
							(value movability_task_planner n0)

							(value barcode_task_planner n2)

			)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value gripper_task_planner ?vgripper_task_planner))
					(value gripper_task_planner n0)
				)
	)

	(:action read_barcode
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value box_task_planner n4)

							(and 
							(value robot_task_planner n2)

							(and 
							(value item_task_planner n1)

							(and 
							(value warehouse_task_planner n3)

							(and 
							(value gripper_task_planner n1)

							(and 
							(value conveyor_task_planner n2)

							(and 
							(value readability_task_planner n0)

							(value barcode_task_planner n0)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value barcode_task_planner ?vbarcode_task_planner))
					(value barcode_task_planner n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner ?vconveyor_task_planner)
			(and 
							(value box_task_planner n5)

							(value robot_task_planner n4)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n1)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner ?vconveyor_task_planner)
			(and 
							(value box_task_planner n5)

							(value robot_task_planner n5)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n1)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner ?vconveyor_task_planner)
			(and 
							(value box_task_planner n5)

							(value robot_task_planner n7)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n1)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner ?vconveyor_task_planner)
			(and 
							(value box_task_planner n6)

							(value robot_task_planner n4)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n1)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner ?vconveyor_task_planner)
			(and 
							(value box_task_planner n6)

							(value robot_task_planner n5)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n1)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value conveyor_task_planner ?vconveyor_task_planner)
			(and 
							(value box_task_planner n6)

							(value robot_task_planner n7)

			)

		)
		:effect
			 1 
				(and 
					(not (value box_task_planner ?vbox_task_planner))
					(value box_task_planner n1)
					(not (value conveyor_task_planner ?vconveyor_task_planner))
					(value conveyor_task_planner n1)
				)
	)

	(:action transport
		:parameters (
		 ?vrobot_task_planner - num
		)
		:precondition (
			and (at l_task_planner)
			(value robot_task_planner ?vrobot_task_planner)
			(and 
							(value item_task_planner n2)

							(and 
							(not (value robot_task_planner n4))

							(and 
							(value gripper_task_planner n2)

							(and 
							(value movability_task_planner n0)

							(value obstacle_task_planner n0)

			)

			)

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n3)
					(not (value robot_task_planner ?vrobot_task_planner))
					(value robot_task_planner n4)
				)
	)

	(:action update_warehouse
		:parameters (
		)
		:precondition (
			and (at l_task_planner)
			(and 
							(value warehouse_task_planner n0)

							(and 
							(value item_task_planner n5)

							(not (value box_task_planner n5))

			)

			)

		)
		:effect
			 1 
				(and 
					(not (value item_task_planner ?vitem_task_planner))
					(value item_task_planner n0)
					(not (value warehouse_task_planner ?vwarehouse_task_planner))
					(value warehouse_task_planner n3)
				)
	)


)