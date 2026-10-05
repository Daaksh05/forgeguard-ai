import unittest

from ai.agent.schemas import AgentInput, AgentOutput, MachineContext, VisualMode


class TestSchemas(unittest.TestCase):
    def test_machine_context_and_agent_input(self):
        machine = MachineContext(machine_id="PUMP_001", operating_state="RUNNING")
        agent_input = AgentInput(machine_info=machine)
        self.assertEqual(agent_input.machine.machine_id, "PUMP_001")
        self.assertEqual(agent_input.machine_info.machine_id, "PUMP_001")

    def test_agent_output_defaults(self):
        output = AgentOutput(
            machine_id="PUMP_001",
            severity="HIGH",
            diagnosis="Bearing issue",
            confidence=0.82,
        )
        self.assertTrue(output.human_approval_required)
        self.assertEqual(output.recommended_actions, [])

    def test_visual_mode_enum(self):
        self.assertEqual(VisualMode.DEMO.value, "DEMO")


if __name__ == "__main__":
    unittest.main()
