class CreateGarageDoorStates < ActiveRecord::Migration
  	def change
	  	create_table :garage_door_states do |t|
	  		t.boolean :fully_open
	  		t.boolean :fully_closed
	  		t.boolean :indoor_button_pressed
	  		t.boolean :web_button_pressed
	  		t.boolean :alarm_on
	  		
	  		t.timestamps
  		end
  	end
end
