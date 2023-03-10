/**********************************************************************************************
 * 
**********************************************************************************************/

#include <ros/ros.h>
#include <string>
#include <pthread.h>
#include <boost/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <unitree_legged_msgs/HighCmd.h>
#include <unitree_legged_msgs/HighState.h>

#include <data_parser.hpp>

#include "convert.h" // Needed for ToRos()

using namespace UNITREE_LEGGED_SDK;


#include <python_interface_go1/real_robot_interface_go1_highlevel.hpp>


class ROSRealRobotInterfaceGo1HighLevel : public RealRobotInterfaceGo1HighLevel {

public:

    ROSRealRobotInterfaceGo1HighLevel() : RealRobotInterfaceGo1HighLevel(){

      std::cout << "Initializing high level communication with the robot ...\n";

    }

    ~ROSRealRobotInterfaceGo1HighLevel(){
        std::cout << "Destroying ROSRealRobotInterfaceGo1HighLevel class ...\n";
    }

    void highCmdCallback(const unitree_legged_msgs::HighCmd::ConstPtr &msg);

};


void ROSRealRobotInterfaceGo1HighLevel::highCmdCallback(const unitree_legged_msgs::HighCmd::ConstPtr &msg){

  // Callback for subscriber to high level commands from the network

  // For now, we only pick up commands related to velocity and modes:
  float vel_linear_forward = msg->velocity[0];
  float vel_linear_sideways = msg->velocity[1];
  float vel_angular = msg->yawSpeed;
  float bodyHeight = msg->bodyHeight;
  this->send_linear_and_angular_velocity_commands(vel_linear_forward,vel_linear_sideways,vel_angular);
  this->send_desired_body_height(bodyHeight);

  return;
}






int main(int argc, char *argv[])
{
  /*
    This node:
    1) Reads the current highlevel robot state and publishes it
    2) Listens to user commands from the network through a subscriber
    3) The class used inherits from RealRobotInterfaceGo1HighLevel, defined in another repo: 
        <catkin_ws>/src/unitree_legged_sdk_from_inside_robot/include/python_interface_go1/real_robot_interface_go1_highlevel.hpp
   */
    
    ros::init(argc, argv, "node_ros_real_robot_interface_go1_highlevel"); // Node name is overriden with field 'name' inside th launch file

    ros::NodeHandle nh;

    // Parsing input arguments:
    DataParser data_parser(nh);
    std::cout << "Loading parameters:\n";
    std::string topic_subscribe_to_user_commands, topic_publish_robot_state;
    data_parser.get("topic_subscribe_to_user_commands",topic_subscribe_to_user_commands);
    data_parser.get("topic_publish_robot_state",topic_publish_robot_state);
    int loop_frequency;
    data_parser.get("loop_frequency",loop_frequency);

    // Set loop frequency:
    ros::Rate loop_rate(loop_frequency); // amarco: Frequency in Hz

    std::cout << "Initializing Go1 interface ...\n";
    std::cout << " * This node has three main functionalities:\n";
    std::cout << "   (1) Initialize the parent class RealRobotInterfaceGo1HighLevel, which \n";
    std::cout << "       communicates with the robot via Unitree's UDP protocols \n";
    std::cout << "   (2) Publish the current high level robot state to the topic " << topic_publish_robot_state << " \n";
    std::cout << "   (3) Subscribe to high-level user commands found at the topic " << topic_subscribe_to_user_commands << " \n";
    std::cout << " * The parent class RealRobotInterfaceGo1HighLevel does not use LCM";
    // std::cout << "Receiving LCM low-level state data from the robot and publishing it ...\n";
    // std::cout << "Subscribing to low-level commands from the network and sending them to the robot via LCM ...\n";

    ROSRealRobotInterfaceGo1HighLevel ros_robot_interface_go1_highlevel;
    ros_robot_interface_go1_highlevel.set_deltaT(1./(double)loop_frequency); // seconds

    // Initialize global variables:
    unitree_legged_msgs::HighState state_msg;
    ros::Publisher pub_low = nh.advertise<unitree_legged_msgs::HighState>(topic_publish_robot_state, 100);
    ros::Subscriber sub_low = nh.subscribe(topic_subscribe_to_user_commands, 100, &ROSRealRobotInterfaceGo1HighLevel::highCmdCallback, &ros_robot_interface_go1_highlevel); // Receive commands from the network


    std::cout << "[WARNING]: Control level is set to HIGHLEVEL." << std::endl
              << " (1) Make sure the robot is standing." << std::endl
              << " (2) Press Enter to start the loop..." << std::endl;
    std::cin.ignore();

    // // This overrides the default sigint handler (must be set after the first node is created):
    // signal(SIGINT, mySigintHandler);

    std::cout << "Publishing the robot state and listening to user commands indefinitely ...\n";
    while (ros::ok()){

        // Receive observations from the robot and update the .state field
        ros_robot_interface_go1_highlevel.get_observations();

        // Publish the current state:
        state_msg = ToRos(ros_robot_interface_go1_highlevel.state);
        pub_low.publish(state_msg);

        ros::spinOnce(); // Go through the callbacks and fill position2hold with the commands collected from the network in ros_robot_interface_go1_highlevel.highCmdCallback()
        loop_rate.sleep();
    }

    std::cout << "Finishing ros_robot_interface_go1_highlevel ...\n";
    delete(&nh); // amarco: not sure if this is the right way...
    ros::shutdown();

    return 0;
}

