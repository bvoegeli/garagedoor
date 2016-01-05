get '/' do
	@current_state = GarageDoorStates.last
	erb :index
end

get '/open_and_close' do
	@output = system('ls')
	# output = `ls` # This wasn't successfully executed the script, left here for future reference
	p @output
	redirect '/'
end