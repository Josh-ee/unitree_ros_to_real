import numpy as np
import pdb

import pickle
import math

import matplotlib.pyplot as plt
import matplotlib

from .generate_vel_profile import get_velocity_profile_given_waypoints

markersize_x0 = 10
markersize_trajs = 0.4
fontsize_labels = 25
matplotlib.rc('xtick', labelsize=fontsize_labels)
matplotlib.rc('ytick', labelsize=fontsize_labels)
matplotlib.rc('text', usetex=False)
# matplotlib.rc('font',**{'family':'serif','serif':['Computer Modern Roman']})
plt.rc('legend',fontsize=fontsize_labels+2)

def cut_data(path2data,subsample_every_nr_steps=1):

	print("Loading {0:s} ...".format(path2data))
	file = open(path2data, 'rb')
	data_dict = pickle.load(file)
	file.close()

	# Use time stamp to tell:
	time_stamp = data_dict["time_stamp"]
	if np.all(time_stamp != 0):
		Ncut = time_stamp.shape[0]
	else:
		Ncut = np.arange(time_stamp.shape[0])[time_stamp[:,0] == 0][0]
		# Ncut = Ncut - 10 # For experiments on 2023_03_13 because we were not resetting to zeros the data2save dictionary in node_data_collection.py
		for key, val in data_dict.items():
			data_dict[key] = val[0:Ncut:subsample_every_nr_steps,:]

	return data_dict

def plot_all(data,path2load,subsample_every_nr_steps=1):

	rate_freq_send_commands = 120 # Hz
	deltaT = 1./rate_freq_send_commands

	for traj_name, traj_dict in data.items():

		name_file_list = data[traj_name]["name_file_list"]
		hdl_splots_dict = None
		for name_file in name_file_list:

			if hdl_splots_dict is None:
				time_tot = data[traj_name]["time_tot"]
				pos_waypoints = data[traj_name]["pos_waypoints"]
				state_tot, vel_tot = get_velocity_profile_given_waypoints(pos_waypoints,deltaT,time_tot,block_plot=False,plotting=False) # state_tot: [Nsteps_tot,2] || vel_tot: [Nsteps_tot,2]

			create_plots_from_scratch = hdl_splots_dict is None
			hdl_splots_dict = plot_single_file(path2load,name_file,create_plots_from_scratch,hdl_splots_dict,state_tot,subsample_every_nr_steps)

	plt.show(block=True)

def plot_single_file(path2load,name_file,create_plots_from_scratch,hdl_splots_dict,state_tot,subsample_every_nr_steps=1):

	path2data = "{0:s}/{1:s}".format(path2load,name_file)
	data_dict = cut_data(path2data,subsample_every_nr_steps)

	time_stamp = data_dict["time_stamp"]
	robot_pos = data_dict["robot_pos"]
	robot_vel = data_dict["robot_vel"]
	robot_orientation = data_dict["robot_orientation"]
	robot_angular_velocity = data_dict["robot_angular_velocity"]
	vel_forward_des = data_dict["vel_forward_des"]
	vel_yaw_des = data_dict["vel_yaw_des"]

	# Velocity profiles:
	if create_plots_from_scratch:
		hdl_fig_data, hdl_splots_data = plt.subplots(3,2,figsize=(12,8),sharex=True)
		hdl_fig_data.suptitle("Robot Pose (from Vicon)",fontsize=fontsize_labels)
		hdl_splots_dict = dict()
		hdl_splots_dict["robot_pose"] = hdl_splots_data
	else:
		hdl_splots_data = hdl_splots_dict["robot_pose"]


	hdl_splots_data[0,0].plot(time_stamp,robot_pos[:,0],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[1,0].plot(time_stamp,robot_pos[:,1],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[2,0].plot(time_stamp,robot_pos[:,2],lw=1,alpha=0.3,color="navy")

	hdl_splots_data[0,1].plot(time_stamp,robot_orientation[:,0],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[1,1].plot(time_stamp,robot_orientation[:,1],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[2,1].plot(time_stamp,robot_orientation[:,2],lw=1,alpha=0.3,color="navy")

	hdl_splots_data[-1,0].set_xlabel("time [sec]",fontsize=fontsize_labels)
	hdl_splots_data[-1,1].set_xlabel("time [sec]",fontsize=fontsize_labels)

	# Velocity profiles:
	if create_plots_from_scratch:
		hdl_fig_data, hdl_splots_data = plt.subplots(3,2,figsize=(12,8),sharex=True)
		hdl_fig_data.suptitle("Robot Velocities (Differentiated Vicon signals)",fontsize=fontsize_labels)
		hdl_splots_dict["robot_velocities"] = hdl_splots_data
	else:
		hdl_splots_data = hdl_splots_dict["robot_velocities"]


	hdl_splots_data[0,0].plot(time_stamp,robot_vel[:,0],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[1,0].plot(time_stamp,robot_vel[:,1],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[2,0].plot(time_stamp,robot_vel[:,2],lw=1,alpha=0.3,color="navy")

	hdl_splots_data[0,1].plot(time_stamp,robot_angular_velocity[:,0],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[1,1].plot(time_stamp,robot_angular_velocity[:,1],lw=1,alpha=0.3,color="navy")
	hdl_splots_data[2,1].plot(time_stamp,robot_angular_velocity[:,2],lw=1,alpha=0.3,color="navy")

	hdl_splots_data[-1,0].set_xlabel("time [sec]",fontsize=fontsize_labels)
	hdl_splots_data[-1,1].set_xlabel("time [sec]",fontsize=fontsize_labels)


	# Velocity profiles:
	if create_plots_from_scratch:
		hdl_fig_data, hdl_splots_data = plt.subplots(2,1,figsize=(12,8),sharex=True)
		hdl_fig_data.suptitle("Robot Control",fontsize=fontsize_labels)
		hdl_splots_dict["robot_control"] = hdl_splots_data
	else:
		hdl_splots_data = hdl_splots_dict["robot_control"]

	robot_vel_curr = np.sqrt(robot_vel[:,0]**2 + robot_vel[:,1]**2)
	hdl_splots_data[0].plot(time_stamp,robot_vel_curr,lw=1,alpha=0.8,color="navy")
	hdl_splots_data[0].plot(time_stamp,vel_forward_des,lw=3,alpha=0.3,color="navy")
	hdl_splots_data[0].set_title("Forward velocity",fontsize=fontsize_labels)

	hdl_splots_data[1].plot(time_stamp,robot_angular_velocity[:,2],lw=1,alpha=0.8,color="navy")
	hdl_splots_data[1].plot(time_stamp,vel_yaw_des,lw=3,alpha=0.3,color="navy")
	hdl_splots_data[1].set_title("Angular velocity",fontsize=fontsize_labels)

	hdl_splots_data[-1].set_xlabel("time [sec]",fontsize=fontsize_labels)

	# Position profile:
	if create_plots_from_scratch:
		hdl_fig_data, hdl_splots_data = plt.subplots(1,1,figsize=(12,8),sharex=True)
		hdl_fig_data.suptitle("Robot XY Position",fontsize=fontsize_labels)
		hdl_splots_dict["robot_xy_position"] = hdl_splots_data
	else:
		hdl_splots_data = hdl_splots_dict["robot_xy_position"]

	hdl_splots_data.plot(robot_pos[:,0],robot_pos[:,1],lw=1.5,alpha=0.4,color="navy")
	hdl_splots_data.plot(state_tot[:,0],state_tot[:,1],lw=3,alpha=0.2,color="crimson")
	hdl_splots_data.set_xlabel("x [m]",fontsize=fontsize_labels)
	hdl_splots_data.set_ylabel("y [m]",fontsize=fontsize_labels)
	hdl_splots_data.set_xlim([-3.0,+2.0])
	hdl_splots_data.set_ylim([-1.0,5.0])

	return hdl_splots_dict


def join_data(data,path2load,save_data_trajs_dict=None,subsample_every_nr_steps=1):

	state_and_control_curr_traj_list = []
	state_next_traj_list = []
	for traj_name, traj_dict in data.items():

		name_file_list = data[traj_name]["name_file_list"]

		state_and_control_curr_list = []
		state_next_list = []
		for name_file in name_file_list:

			path2data = "{0:s}/{1:s}".format(path2load,name_file)
			data_dict = cut_data(path2data,subsample_every_nr_steps)
			
			time_stamp = data_dict["time_stamp"]
			robot_pos = data_dict["robot_pos"]
			robot_vel = data_dict["robot_vel"]
			robot_orientation = data_dict["robot_orientation"]
			robot_angular_velocity = data_dict["robot_angular_velocity"]
			vel_forward_des = data_dict["vel_forward_des"]
			vel_yaw_des = data_dict["vel_yaw_des"]

			state_and_control_curr_list += [np.concatenate([robot_pos[0:-1,0:2],robot_orientation[0:-1,2:3],vel_forward_des[0:-1,:],vel_yaw_des[0:-1,:]],axis=1)] # [state: (x,y,th), control=(u_for,u_ang)]
			state_next_list += [np.concatenate([robot_pos[1::,0:2],robot_orientation[1::,2:3]],axis=1)]

		state_and_control_curr_traj_list += [np.concatenate(state_and_control_curr_list,axis=0)]
		state_next_traj_list += [np.concatenate(state_next_list,axis=0)]

	state_and_control_curr = np.concatenate(state_and_control_curr_traj_list,axis=0)
	state_next_traj = np.concatenate(state_next_traj_list,axis=0)

	if save_data_trajs_dict:
		name_file2save = "joined_go1trajs.pickle"
		data2save = dict(Xtrain=state_and_control_curr,Ytrain=state_next_traj)
		path2save = path2load
		path2save_full = "{0:s}/{1:s}".format(path2save,name_file2save)
		print("Saving data at {0:s} ...".format(path2save_full))
		file = open(path2save_full, 'wb')
		pickle.dump(data2save,file)
		file.close()
		print("Done saving data!")

	return state_and_control_curr, state_next_traj
