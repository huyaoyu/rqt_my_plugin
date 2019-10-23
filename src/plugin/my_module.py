import os
import rospy
import rospkg
from std_msgs.msg import String

from qt_gui.plugin import Plugin
from python_qt_binding import loadUi
from python_qt_binding.QtCore import Qt, Slot
from python_qt_binding.QtWidgets import QWidget

from my_plugin.srv import AddTwoInts, AddTwoIntsResponse

class MyPlugin(Plugin):

    def __init__(self, context):
        super(MyPlugin, self).__init__(context)
        # Give QObjects reasonable names
        self.setObjectName('MyPlugin')

        # Process standalone plugin command-line arguments
        from argparse import ArgumentParser
        parser = ArgumentParser()
        # Add argument(s) to the parser.
        parser.add_argument("-q", "--quiet", action="store_true",
                      dest="quiet",
                      help="Put plugin in silent mode")
        args, unknowns = parser.parse_known_args(context.argv())
        if not args.quiet:
            print 'arguments: ', args
            print 'unknowns: ', unknowns

        # Create QWidget
        self._widget = QWidget()
        # Get path to UI file which should be in the "resource" folder of this package
        ui_file = os.path.join(rospkg.RosPack().get_path('my_plugin'), 'resource', 'MyPlugin.ui')
        # Extend the widget with all attributes and children from UI file
        loadUi(ui_file, self._widget)
        # Give QObjects reasonable names
        self._widget.setObjectName('MyPluginUi')
        # Show _widget.windowTitle on left-top of each plugin (when 
        # it's set in _widget). This is useful when you open multiple 
        # plugins at once. Also if you open multiple instances of your 
        # plugin at once, these lines add number to make it easy to 
        # tell from pane to pane.
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))
        
        # Push button.
        self._widget.button_test.clicked.connect(self.on_button_test_clicked)
        
        # Add widget to the user interface
        context.add_widget(self._widget)

        # Simple topic publisher from ROS tutorial.
        self.rosPub = rospy.Publisher('my_plugin_pub', String, queue_size=10)
        self.rosPubCount = 0

        # Simple topic subscriber.
        self.rosSub = rospy.Subscriber("my_plugin_sub", String, self.ros_string_handler)

        # Start simple ROS server.
        self.rosSrv = rospy.Service("add_two_ints", AddTwoInts, self.handle_add_two_ints)

    def ros_string_handler(self, data):
        rospy.loginfo(rospy.get_caller_id() + ": Subscriber receives %s", data.data)

    def handle_add_two_ints(self, req):
        rospy.loginfo( "Returning [%s + %s = %s]" % (req.a, req.b, (req.a + req.b)) )
        return AddTwoIntsResponse(req.a + req.b)

    @Slot()
    def on_button_test_clicked(self):
        rospy.loginfo("button_test gets clicked. Send request to itself.")

        self.rosPub.publish("rosPubCount = %d. " % (self.rosPubCount))
        self.rosPubCount += 1

        # Send service request.
        try:
            rospy.wait_for_service("add_two_ints", timeout=5)

            # Set the actual request.
            add_two_ints = rospy.ServiceProxy('add_two_ints', AddTwoInts)
            resp = add_two_ints(self.rosPubCount, 100)

            rospy.loginfo("add_two_ints responses with %d. " % ( resp.sum ))
        except rospy.ROSException as e:
            rospy.loginfo("Service add_two_ints unavailable for 5 seconds.")
        except rospy.ServiceException as e:
            rospy.logerr("Service request to add_two_ints failed.")

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        self.rosSrv.shutdown()
        rospy.loginfo("rosSrv shutdown. ")

        self.rosSub.unregister()
        rospy.loginfo("rosSub unregistered. ")

        self.rosPub.unregister()
        rospy.loginfo("rosPub unregistered. ")

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    #def trigger_configuration(self):
        # Comment in to signal that the plugin has a way to configure
        # This will enable a setting button (gear icon) in each dock widget title bar
        # Usually used to open a modal configuration dialog
        