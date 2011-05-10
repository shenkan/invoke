import unittest
import new
from should_dsl import should, should_not
from fluidity.machine import StateMachine, state, event


class ActionMachine(StateMachine):

      state('created', exit='post_create')
      state('waiting', enter='pre_wait')
      initial_state = 'created'
      event('queue', from_='created', to='waiting')

      def __init__(self):
          super(ActionMachine, self).__init__()
          self.is_enter_aware = False
          self.is_exit_aware = False
          self.count = 0

      def pre_wait(self):
          self.is_enter_aware = True
          if getattr(self, 'pre_wait_expectation', None):
              self.pre_wait_expectation()

      def post_create(self):
          self.is_exit_aware = True
          if getattr(self, 'post_create_expectation', None):
              self.post_create_expectation()


class FluidityAction(unittest.TestCase):

      def it_runs_enter_action_before_machine_enters_a_given_state(self):
          machine = ActionMachine()
          machine |should_not| be_enter_aware
          machine.queue()
          machine |should| be_enter_aware

      def it_runs_exit_action_after_machine_exits_a_given_state(self):
          machine = ActionMachine()
          machine |should_not| be_exit_aware
          machine.queue()
          machine |should| be_enter_aware

      def it_runs_exit_action_before_enter_action(self):
          '''it runs old state's exit action before new state's enter action'''
          machine = ActionMachine()
          def post_create_expectation(_self):
              _self.count +=1
              _self.count |should| be(1)
          def pre_wait_expectation(_self):
              _self.count += 1
              _self.count |should| be(2)
          machine.post_create_expectation = new.instancemethod(
              post_create_expectation, machine, ActionMachine)
          machine.pre_wait_expectation = new.instancemethod(
              pre_wait_expectation, machine, ActionMachine)
          machine.queue()
