from nose.plugins.base import Plugin
from testlink import TestLinkClient
from testlink.common import status

from functools import wraps
from datetime import datetime

import logging

log = logging.getLogger(__name__)
TESTLINK_ATTRS = ['testlink_id', 'project_name', 'plan_name']
TEST_QUEUE = []

def current_date_string():
    """
    Get the current date as a string. Used for
    making a new build which this plugin runs
    """
    return datetime.utcnow().strftime("%Y-%m-%dt%H:%M:%S")


def testlink_task(_id, project_name = None, plan_name = None):
    """
    Decorator that denotes that a test is linked to
    a testlink entry
    """
    def test(fn):
        @wraps(fn)
        def innerdef(*args, **kwargs):
            
            #Keep a top level queue of attributes,
            #must be popped when accessed
            TEST_QUEUE.append({
                'testlink_id': _id,
                'project_name': project_name,
                'plan_name': plan_name
                })
            
            return fn(*args, **kwargs)
        return innerdef
    return test


class TestlinkPlugin(Plugin):
    name = 'testlink'
    enabled = True
    
    def options(self, parser, env):
        """Add API key/value to the parser"""
        Plugin.options(self, parser, env)
        parser.add_option(
            "--testlink-endpoint", action="store",
            dest="testlink_endpoint", default="http://localhost/lib/api/v1/xmlapi.php",
            help="""
            API endpoint for communicating with your Testlink instance
            """)
        parser.add_option(
            "--testlink-key", action="store",
            dest="testlink_key", default=None,
            help="""
            Developer key for accessing your Testlink API
            """)
        parser.add_option(
            "--plan-name", action="store",
            dest="plan_name", default=None,
            help = """
            Test plan name for this run
            """)
        parser.add_option(
            "--project-name", action="store",
            dest="project_name", default=None,
            help = """
            Test plan name for this run
            """)
        parser.add_option(
            "--build-name", action="store",
            dest="build_name", default=None,
            help = """
            The build name for this run. Note if this is not
            given or not found, it will automatically create one
            """
            )
        parser.add_option(
            "--platform-name", action="store",
            dest="platform_name", default=None,
            help="""
            The platform to associate with this run
            """
            )

        
    def configure(self, options, config):
        """
        Generate the classes' access to the API
        via the options
        """
        requirements = ['project_name', 'plan_name',
                        'testlink_endpoint', 'testlink_key',
                        'platform_name']
        self.valid = reduce(lambda a, b: a and b,
                      map (lambda x: getattr(options, x),
                           requirements
                           )
                        )        
        if not self.valid:
            log.warning("Testlink nose plugin is not configured properly")
            return
        self.api = TestLinkClient(options.testlink_endpoint, options.testlink_key)
        self.project_name = options.project_name
        self.plan_name = options.plan_name
        self.build_name = options.build_name
        self.platform_name = options.platform_name
        self.plan = self.api.projects.get(self.project_name).plans.get(name=self.plan_name)

        #Make the build if it isn't specified
        if not self.build_name:
            self.build_name = "Build-{}".format(current_date_string())
            self.plan.builds.create(self.build_name, notes="Automated by nose")
            
                        
    def _set_execution_result(self, test, status, notes=None):
        """
        Sets the execution result of the test to status
        """
        if not self.valid or not len(TEST_QUEUE):
            #Was not specified
            return
        
        params = {
            'build_name': self.build_name,
            'overwrite': False
            }
        test_settings = TEST_QUEUE.pop()        
        if notes:
            params['notes'] = notes

        #First get the test
        project_name = test_settings.get('project_name', None) or self.project_name
        plan_name = test_settings.get('plan_name', None)
        if plan_name:
            plan = self.api.projects.get(project_name).plans.get(name=plan_name)
        else:
            plan = self.plan
        test = plan.cases.get(external_id=test_settings.get('testlink_id'))
        return test.report(status,  **params)
        
        
    def addSuccess(self, test, capt):
        """
        Updates the test case as successful
        """
        self._set_execution_result(test, status.PASSED)
                                   
        
    def addError(self, test, err):
        """
        Updates the test as failed
        """
        self._set_execution_result(test, status.FAILED)


    def addFailure(self, test, err):
        """
        Updates the test as failed
        """
        self._set_execution_result(test, status.FAILED)

