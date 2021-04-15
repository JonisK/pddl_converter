; mdp
(define (domain saint_reduced_auto)
	(:types int  loc  bool  num)
	(:constants
		goal_condition - bool
		obstacle - int
		sorter - int
		conveyor - int
		gripper - int
		box_detectability - int
		warehouse - int
		graspability - int
		box - int
		movability - int
		readability - int
		robot - int
		item - int
		item_detectability - int
		barcode - int
		location_task_planner - loc
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
	(:action request_box
		:parameters (
		 ?vconveyor - num
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor ?vconveyor)
			(and 
							(value box n5)

							(value robot n4)

			)

		)
		:effect
				(and 
					(not (value box n6))
					(value box n1)
					(not (value conveyor ?vconveyor))
					(value conveyor n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor - num
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor ?vconveyor)
			(and 
							(value box n5)

							(value robot n5)

			)

		)
		:effect
				(and 
					(not (value box n6))
					(value box n1)
					(not (value conveyor ?vconveyor))
					(value conveyor n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor - num
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor ?vconveyor)
			(and 
							(value box n5)

							(value robot n7)

			)

		)
		:effect
				(and 
					(not (value box n6))
					(value box n1)
					(not (value conveyor ?vconveyor))
					(value conveyor n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor - num
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor ?vconveyor)
			(and 
							(value box n6)

							(value robot n4)

			)

		)
		:effect
				(and 
					(not (value box n6))
					(value box n1)
					(not (value conveyor ?vconveyor))
					(value conveyor n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor - num
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor ?vconveyor)
			(and 
							(value box n6)

							(value robot n5)

			)

		)
		:effect
				(and 
					(not (value box n6))
					(value box n1)
					(not (value conveyor ?vconveyor))
					(value conveyor n1)
				)
	)

	(:action request_box
		:parameters (
		 ?vconveyor - num
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor ?vconveyor)
			(and 
							(value box n6)

							(value robot n7)

			)

		)
		:effect
				(and 
					(not (value box n6))
					(value box n1)
					(not (value conveyor ?vconveyor))
					(value conveyor n1)
				)
	)

	(:action box_arrived
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value box n1)

							(value conveyor n1)

			)

		)
		:effect
				(and 
					(not (value box n1))
					(value box n2)
					(not (value conveyor n1))
					(value conveyor n2)
				)
	)

	(:action move_to_find_box_pose
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value movability n0)

							(and 
							(value robot n7)

							(and 
							(value obstacle n0)

							(value gripper n1)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot n7))
					(value robot n1)
				)
	)

	(:action detect_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value warehouse n2)

							(and 
							(value box_detectability n0)

							(and 
							(value robot n1)

							(and 
							(value conveyor n2)

							(and 
							(value box n0)

							(value gripper n1)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n2))
					(value box n3)
				)
	)

	(:action detect_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value warehouse n2)

							(and 
							(value box_detectability n0)

							(and 
							(value robot n1)

							(and 
							(value conveyor n2)

							(and 
							(value box n2)

							(value gripper n1)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n2))
					(value box n3)
				)
	)

	(:action get_box_info
		:parameters (
		 ?vwarehouse - num
		)
		:precondition (
			and (at location_task_planner)
			(value warehouse ?vwarehouse)
			(value box n3)

		)
		:effect
				(and 
					(not (value box n3))
					(value box n4)
					(not (value warehouse ?vwarehouse))
					(value warehouse n3)
				)
	)

	(:action move_to_inspect_box_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(not (value robot n2))

							(and 
							(value conveyor n2)

							(and 
							(value gripper n1)

							(and 
							(value box n4)

							(value obstacle n0)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot ?vrobot))
					(value robot n2)
				)
	)

	(:action detect_item
		:parameters (
		 ?vitem - num
		)
		:precondition (
			and (at location_task_planner)
			(value item ?vitem)
			(and 
							(value movability n0)

							(and 
							(value item_detectability n0)

							(and 
							(value warehouse n3)

							(and 
							(value robot n2)

							(and 
							(value conveyor n2)

							(and 
							(value gripper n1)

							(and 
							(not (value item n1))

							(value box n4)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item ?vitem))
					(value item n1)
				)
	)

	(:action detect_item
		:parameters (
		 ?vitem - num
		)
		:precondition (
			and (at location_task_planner)
			(value item ?vitem)
			(and 
							(value movability n0)

							(and 
							(value item_detectability n0)

							(and 
							(value warehouse n4)

							(and 
							(value robot n2)

							(and 
							(value conveyor n2)

							(and 
							(value gripper n1)

							(and 
							(not (value item n1))

							(value box n4)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item ?vitem))
					(value item n1)
				)
	)

	(:action read_barcode
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value readability n0)

							(and 
							(value warehouse n3)

							(and 
							(value robot n2)

							(and 
							(value conveyor n2)

							(and 
							(value gripper n1)

							(and 
							(value box n4)

							(and 
							(value item n1)

							(value barcode n0)

			)

			)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value barcode n0))
					(value barcode n1)
				)
	)

	(:action check_barcode
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value barcode n1)

							(value warehouse n3)

			)

		)
		:effect
				(and 
					(not (value warehouse n3))
					(value warehouse n4)
					(not (value barcode n1))
					(value barcode n2)
				)
	)

	(:action grasp
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value movability n0)

							(and 
							(value graspability n0)

							(and 
							(value warehouse n4)

							(and 
							(value robot n2)

							(and 
							(value conveyor n2)

							(and 
							(value gripper n1)

							(and 
							(value box n4)

							(and 
							(value item n1)

							(value barcode n2)

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
				(and 
					(not (value item n1))
					(value item n2)
					(not (value gripper n1))
					(value gripper n2)
					(not (value robot n2))
					(value robot n3)
				)
	)

	(:action transport
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(not (value robot n4))

							(and 
							(value gripper n2)

							(and 
							(value item n2)

							(value obstacle n0)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot ?vrobot))
					(value robot n4)
					(not (value item n2))
					(value item n3)
				)
	)

	(:action check_gripper_occupied
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value movability n0)

							(and 
							(value gripper n2)

							(value item n3)

			)

			)

		)
		:effect
				(and 
					(not (value item n3))
					(value item n2)
				)
	)

	(:action move_to_place_pose
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value movability n0)

							(and 
							(value robot n4)

							(and 
							(value sorter n1)

							(and 
							(value item n2)

							(value obstacle n0)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot n4))
					(value robot n5)
				)
	)

	(:action place
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value movability n0)

							(and 
							(value warehouse n4)

							(and 
							(value robot n5)

							(and 
							(value sorter n1)

							(and 
							(value gripper n2)

							(and 
							(value item n2)

							(value barcode n2)

			)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item n2))
					(value item n0)
					(not (value gripper n2))
					(value gripper n0)
				)
	)

	(:action check_gripper_free
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value movability n0)

							(and 
							(value warehouse n4)

							(and 
							(value robot n5)

							(and 
							(value item n0)

							(value gripper n0)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item n0))
					(value item n5)
					(not (value gripper n0))
					(value gripper n1)
					(not (value warehouse n4))
					(value warehouse n0)
				)
	)

	(:action update_warehouse
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value warehouse n0)

							(and 
							(value item n5)

							(not (value box n5))

			)

			)

		)
		:effect
				(and 
					(not (value item n5))
					(value item n0)
					(not (value warehouse n0))
					(value warehouse n3)
				)
	)

	(:action get_decommission_info
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value warehouse n5)

							(and 
							(value box n4)

							(value gripper n1)

			)

			)

		)
		:effect
				(and 
					(not (value warehouse n5))
					(value warehouse n6)
				)
	)

	(:action move_to_check_empty_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(not (value robot n6))

							(and 
							(value conveyor n2)

							(and 
							(value gripper n1)

							(and 
							(value box n4)

							(value obstacle n0)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot ?vrobot))
					(value robot n6)
				)
	)

	(:action check_empty
		:parameters (
		 ?vitem - num
		 ?vbarcode - num
		)
		:precondition (
			and (at location_task_planner)
			(value barcode ?vbarcode)
			(value item ?vitem)
			(and 
							(value warehouse n6)

							(and 
							(value robot n6)

							(and 
							(value conveyor n2)

							(and 
							(value box n4)

							(value gripper n1)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n4))
					(value box n5)
					(not (value item ?vitem))
					(value item n0)
					(not (value warehouse n6))
					(value warehouse n1)
					(not (value barcode ?vbarcode))
					(value barcode n0)
				)
	)

	(:action move_home
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(value obstacle n0)

							(value conveyor n2)

			)

			)

		)
		:effect
				(and 
					(not (value robot ?vrobot))
					(value robot n7)
				)
	)

	(:action facility_explore_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(value box n0)

		)
		:effect
				(and 
					(not (value box n0))
					(value box n2)
				)
	)

	(:action facility_explore_conveyor
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(value conveyor n0)

		)
		:effect
				(and 
					(not (value conveyor n0))
					(value conveyor n2)
				)
	)

	(:action facility_explore_sorter
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(value sorter n0)

		)
		:effect
				(and 
					(not (value sorter n0))
					(value sorter n1)
				)
	)

	(:action explore_gripper
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value gripper n0)

							(value movability n0)

			)

		)
		:effect
				(and 
					(not (value gripper n0))
					(value gripper n1)
				)
	)

	(:action move_to_find_obstacle_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(not (value robot n8))

							(and 
							(value obstacle n1)

							(value conveyor n2)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot ?vrobot))
					(value robot n8)
				)
	)

	(:action detect_obstacle
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value robot n8)

							(and 
							(value conveyor n2)

							(and 
							(value obstacle n1)

							(value gripper n1)

			)

			)

			)

		)
		:effect
				(and 
					(not (value obstacle n1))
					(value obstacle n0)
				)
	)

	(:action flip_item
		:parameters (
		 ?vitem - num
		 ?vitem_detectability - num
		 ?vreadability - num
		 ?vgraspability - num
		)
		:precondition (
			and (at location_task_planner)
			(value readability ?vreadability)
			(value item ?vitem)
			(value graspability ?vgraspability)
			(value item_detectability ?vitem_detectability)
			(and 
							(value movability n0)

							(and 
							(value robot n2)

							(and 
							(value gripper n1)

							(and 
							(value box n4)

							(value conveyor n2)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item ?vitem))
					(value item n0)
					(not (value gripper n1))
					(value gripper n0)
					(not (value readability ?vreadability))
					(value readability n0)
					(not (value graspability ?vgraspability))
					(value graspability n0)
					(not (value item_detectability ?vitem_detectability))
					(value item_detectability n0)
				)
	)

	(:action blind_grasp
		:parameters (
		 ?vitem - num
		 ?vreadability - num
		 ?vgraspability - num
		)
		:precondition (
			and (at location_task_planner)
			(value readability ?vreadability)
			(value item ?vitem)
			(value graspability ?vgraspability)
			(and 
							(value movability n0)

							(and 
							(value warehouse n4)

							(and 
							(value item_detectability n2)

							(and 
							(value robot n2)

							(and 
							(value gripper n1)

							(and 
							(value box n4)

							(value conveyor n2)

			)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item ?vitem))
					(value item n2)
					(not (value readability ?vreadability))
					(value readability n0)
					(not (value graspability ?vgraspability))
					(value graspability n0)
					(not (value robot n2))
					(value robot n3)
					(not (value item_detectability n2))
					(value item_detectability n0)
				)
	)

	(:action drop_item_in_box
		:parameters (
		 ?vitem - num
		)
		:precondition (
			and (at location_task_planner)
			(value item ?vitem)
			(and 
							(value movability n0)

							(and 
							(value robot n2)

							(and 
							(value gripper n2)

							(and 
							(value conveyor n2)

							(and 
							(not (value item n0))

							(value box n4)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item ?vitem))
					(value item n0)
					(not (value gripper n2))
					(value gripper n1)
				)
	)

	(:action drop_item_in_box
		:parameters (
		 ?vitem - num
		)
		:precondition (
			and (at location_task_planner)
			(value item ?vitem)
			(and 
							(value movability n0)

							(and 
							(value robot n3)

							(and 
							(value gripper n2)

							(and 
							(value conveyor n2)

							(and 
							(not (value item n0))

							(value box n4)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value item ?vitem))
					(value item n0)
					(not (value gripper n2))
					(value gripper n1)
				)
	)

	(:action dispose_item
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value item n0)

							(value gripper n2)

			)

		)
		:effect
				(and 
					(not (value item n0))
					(value item n0)
					(not (value gripper n2))
					(value gripper n1)
				)
	)

	(:action adapt_find_box_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(value box_detectability n1)

							(and 
							(value obstacle n0)

							(value gripper n1)

			)

			)

			)

		)
		:effect
				(and 
					(not (value robot ?vrobot))
					(value robot n1)
					(not (value box_detectability n1))
					(value box_detectability n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(value warehouse n3)

							(and 
							(value item_detectability n1)

							(and 
							(value conveyor n2)

							(value gripper n1)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value readability n1))
					(value readability n0)
					(not (value robot ?vrobot))
					(value robot n2)
					(not (value item_detectability n1))
					(value item_detectability n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(value warehouse n4)

							(and 
							(value item_detectability n1)

							(and 
							(value conveyor n2)

							(value gripper n1)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value readability n1))
					(value readability n0)
					(not (value robot ?vrobot))
					(value robot n2)
					(not (value item_detectability n1))
					(value item_detectability n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(value warehouse n3)

							(and 
							(value readability n1)

							(and 
							(value conveyor n2)

							(value gripper n1)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value readability n1))
					(value readability n0)
					(not (value robot ?vrobot))
					(value robot n2)
					(not (value item_detectability n1))
					(value item_detectability n0)
				)
	)

	(:action adapt_inspect_box_pose
		:parameters (
		 ?vrobot - num
		)
		:precondition (
			and (at location_task_planner)
			(value robot ?vrobot)
			(and 
							(value movability n0)

							(and 
							(value warehouse n4)

							(and 
							(value readability n1)

							(and 
							(value conveyor n2)

							(value gripper n1)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value readability n1))
					(value readability n0)
					(not (value robot ?vrobot))
					(value robot n2)
					(not (value item_detectability n1))
					(value item_detectability n0)
				)
	)

	(:action adapt_grasp_parameters
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value graspability n1)

							(and 
							(value warehouse n4)

							(and 
							(value conveyor n2)

							(and 
							(value box n4)

							(and 
							(value item n1)

							(value barcode n2)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value graspability n1))
					(value graspability n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value box_detectability n2)

							(and 
							(value warehouse n2)

							(and 
							(value robot n1)

							(and 
							(value gripper n1)

							(and 
							(value box n0)

							(value conveyor n2)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n2))
					(value box n3)
					(not (value box_detectability n2))
					(value box_detectability n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value box_detectability n2)

							(and 
							(value warehouse n2)

							(and 
							(value robot n7)

							(and 
							(value gripper n1)

							(and 
							(value box n0)

							(value conveyor n2)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n2))
					(value box n3)
					(not (value box_detectability n2))
					(value box_detectability n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value box_detectability n2)

							(and 
							(value warehouse n2)

							(and 
							(value robot n1)

							(and 
							(value gripper n1)

							(and 
							(value box n2)

							(value conveyor n2)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n2))
					(value box n3)
					(not (value box_detectability n2))
					(value box_detectability n0)
				)
	)

	(:action facility_detect_box
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(and 
							(value box_detectability n2)

							(and 
							(value warehouse n2)

							(and 
							(value robot n7)

							(and 
							(value gripper n1)

							(and 
							(value box n2)

							(value conveyor n2)

			)

			)

			)

			)

			)

		)
		:effect
				(and 
					(not (value box n2))
					(value box n3)
					(not (value box_detectability n2))
					(value box_detectability n0)
				)
	)

	(:action facility_reset_motion
		:parameters (
		)
		:precondition (
			and (at location_task_planner)
			(value movability n1)

		)
		:effect
				(and 
					(not (value movability n1))
					(value movability n0)
				)
	)


)