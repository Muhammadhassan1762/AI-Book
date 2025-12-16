#!/usr/bin/env python3
"""
VLA Context Manager Node for VLA System

This node manages execution context across the VLA pipeline,
tracking state, history, and environmental information.
"""

import rclpy
from rclpy.node import Node
from vla_interfaces.msg import VLACommand, VLAActionSequence, VLAAction, VLAStatus
from vla_interfaces.srv import ProcessCommand, PlanActions, ValidateSafety
from std_msgs.msg import String, Header
from builtin_interfaces.msg import Time
from typing import Dict, List, Any, Optional, Tuple
import time
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


@dataclass
class CommandContext:
    """Context for a single command"""
    command_id: str
    command_text: str
    timestamp: float
    intent: str
    parameters: List[str]
    confidence: float
    action_sequence_id: Optional[str] = None
    status: str = "PENDING"
    progress: float = 0.0
    error_message: str = ""


@dataclass
class ActionContext:
    """Context for a single action"""
    action_id: str
    action_type: str
    parameters: List[str]
    status: str = "PENDING"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    error_message: str = ""


@dataclass
class PipelineContext:
    """Context for an entire pipeline execution"""
    pipeline_id: str
    command_context: CommandContext
    action_contexts: List[ActionContext]
    start_time: float
    end_time: Optional[float] = None
    status: str = "RUNNING"
    progress: float = 0.0
    error_message: str = ""


class VLAContextManagerNode(Node):
    def __init__(self):
        super().__init__('vla_context_manager_node')

        # Declare parameters
        self.declare_parameter('enable_context_tracking', True)
        self.declare_parameter('context_retention_time', 300.0)  # 5 minutes
        self.declare_parameter('enable_context_sharing', True)
        self.declare_parameter('max_context_history', 50)
        self.declare_parameter('context_update_frequency', 1.0)  # seconds
        self.declare_parameter('enable_persistence', False)
        self.declare_parameter('persistence_file', '/tmp/vla_context.json')
        self.declare_parameter('enable_debug', False)
        self.declare_parameter('log_level', 'INFO')

        # Get parameters
        self.enable_context_tracking = self.get_parameter('enable_context_tracking').value
        self.context_retention_time = self.get_parameter('context_retention_time').value
        self.enable_context_sharing = self.get_parameter('enable_context_sharing').value
        self.max_context_history = self.get_parameter('max_context_history').value
        self.context_update_frequency = self.get_parameter('context_update_frequency').value
        self.enable_persistence = self.get_parameter('enable_persistence').value
        self.persistence_file = self.get_parameter('persistence_file').value
        self.enable_debug = self.get_parameter('enable_debug').value

        # Initialize context storage
        self.command_contexts: Dict[str, CommandContext] = {}
        self.action_contexts: Dict[str, ActionContext] = {}
        self.pipeline_contexts: Dict[str, PipelineContext] = {}
        self.current_pipeline_id: Optional[str] = None
        self.current_command_id: Optional[str] = None

        # Create subscribers for tracking pipeline events
        self.command_sub = self.create_subscription(
            VLACommand,
            '/vla/command',
            self.command_callback,
            10
        )

        self.action_sequence_sub = self.create_subscription(
            VLAActionSequence,
            '/vla/action_sequence',
            self.action_sequence_callback,
            10
        )

        self.status_sub = self.create_subscription(
            VLAStatus,
            '/vla/status',
            self.status_callback,
            10
        )

        # Create service for context queries
        self.get_context_srv = self.create_service(
            ProcessCommand,
            '/vla/get_context',
            self.get_context_callback
        )

        # Timer for context cleanup
        self.cleanup_timer = self.create_timer(
            self.context_retention_time / 2,  # Run cleanup halfway through retention time
            self.cleanup_old_contexts
        )

        # Load persisted context if enabled
        if self.enable_persistence:
            self.load_persisted_context()

        self.get_logger().info('VLA Context Manager node initialized')

    def command_callback(self, msg):
        """Callback for command messages"""
        if not self.enable_context_tracking:
            return

        command_id = self.generate_context_id()
        command_context = CommandContext(
            command_id=command_id,
            command_text=msg.command_text,
            timestamp=time.time(),
            intent=msg.intent,
            parameters=msg.parameters.copy(),
            confidence=msg.confidence_score
        )

        self.command_contexts[command_id] = command_context
        self.current_command_id = command_id

        self.get_logger().debug(f'Created context for command: {command_id[:8]} - "{msg.command_text}"')

        # Update current pipeline if one is active
        if self.current_pipeline_id and self.current_pipeline_id in self.pipeline_contexts:
            pipeline_ctx = self.pipeline_contexts[self.current_pipeline_id]
            pipeline_ctx.command_context = command_context
            pipeline_ctx.progress = 10.0  # Initial progress

    def action_sequence_callback(self, msg):
        """Callback for action sequence messages"""
        if not self.enable_context_tracking:
            return

        if not self.current_command_id:
            self.get_logger().warn('Received action sequence without active command')
            return

        # Update command context with action sequence reference
        command_ctx = self.command_contexts[self.current_command_id]
        command_ctx.action_sequence_id = self.generate_context_id()
        command_ctx.status = "PLANNED"
        command_ctx.progress = 50.0

        # Create action contexts for each action in the sequence
        action_contexts = []
        for i, action in enumerate(msg.actions):
            action_id = f"{command_ctx.command_id}_action_{i}"
            action_context = ActionContext(
                action_id=action_id,
                action_type=action.action_type,
                parameters=action.action_parameters.copy(),
                status="PENDING"
            )
            self.action_contexts[action_id] = action_context
            action_contexts.append(action_context)

        # Create pipeline context
        pipeline_id = self.generate_context_id()
        pipeline_context = PipelineContext(
            pipeline_id=pipeline_id,
            command_context=command_ctx,
            action_contexts=action_contexts,
            start_time=time.time(),
            status="RUNNING",
            progress=50.0
        )

        self.pipeline_contexts[pipeline_id] = pipeline_context
        self.current_pipeline_id = pipeline_id

        self.get_logger().debug(f'Created pipeline context: {pipeline_id[:8]} with {len(action_contexts)} actions')

    def status_callback(self, msg):
        """Callback for status messages"""
        if not self.enable_context_tracking:
            return

        if not self.current_pipeline_id or self.current_pipeline_id not in self.pipeline_contexts:
            return

        pipeline_ctx = self.pipeline_contexts[self.current_pipeline_id]
        pipeline_ctx.status = msg.current_state
        pipeline_ctx.progress = msg.progress_percentage

        # Update current action status if available
        if pipeline_ctx.action_contexts and msg.current_action:
            # Find the current action and update its status
            for action_ctx in pipeline_ctx.action_contexts:
                if action_ctx.action_type in msg.current_action or msg.current_action in action_ctx.action_type:
                    if msg.current_state == "EXECUTING":
                        action_ctx.status = "RUNNING"
                        if action_ctx.start_time is None:
                            action_ctx.start_time = time.time()
                    elif msg.current_state == "COMPLETED":
                        action_ctx.status = "COMPLETED"
                        action_ctx.end_time = time.time()
                    elif msg.current_state == "ERROR":
                        action_ctx.status = "FAILED"
                        action_ctx.error_message = msg.error_message
                        action_ctx.end_time = time.time()
                    break

        # Update command context status
        if self.current_command_id in self.command_contexts:
            command_ctx = self.command_contexts[self.current_command_id]
            command_ctx.status = msg.current_state
            command_ctx.progress = msg.progress_percentage
            if msg.error_message:
                command_ctx.error_message = msg.error_message

        # Check if pipeline is complete
        if msg.current_state in ["COMPLETED", "ERROR"]:
            pipeline_ctx.status = msg.current_state
            pipeline_ctx.end_time = time.time()
            if msg.error_message:
                pipeline_ctx.error_message = msg.error_message

    def get_context_callback(self, request, response):
        """Service callback to retrieve context information"""
        try:
            if request.raw_command == "current_pipeline":
                # Return current pipeline context
                if self.current_pipeline_id and self.current_pipeline_id in self.pipeline_contexts:
                    pipeline_ctx = self.pipeline_contexts[self.current_pipeline_id]
                    response.success = True
                    response.processed_command = json.dumps(asdict(pipeline_ctx))
                    response.intent = pipeline_ctx.status
                    response.parameters = [str(pipeline_ctx.progress)]
                    response.error_message = pipeline_ctx.error_message
                    response.error_code = 0
                else:
                    response.success = False
                    response.error_message = "No active pipeline"
                    response.error_code = 2
            elif request.raw_command == "current_command":
                # Return current command context
                if self.current_command_id and self.current_command_id in self.command_contexts:
                    command_ctx = self.command_contexts[self.current_command_id]
                    response.success = True
                    response.processed_command = json.dumps(asdict(command_ctx))
                    response.intent = command_ctx.status
                    response.parameters = [str(command_ctx.progress)]
                    response.error_message = command_ctx.error_message
                    response.error_code = 0
                else:
                    response.success = False
                    response.error_message = "No active command"
                    response.error_code = 2
            elif request.raw_command.startswith("pipeline_"):
                # Return specific pipeline context
                pipeline_id = request.raw_command[9:]  # Remove "pipeline_" prefix
                if pipeline_id in self.pipeline_contexts:
                    pipeline_ctx = self.pipeline_contexts[pipeline_id]
                    response.success = True
                    response.processed_command = json.dumps(asdict(pipeline_ctx))
                    response.intent = pipeline_ctx.status
                    response.parameters = [str(pipeline_ctx.progress)]
                    response.error_message = pipeline_ctx.error_message
                    response.error_code = 0
                else:
                    response.success = False
                    response.error_message = f"Pipeline not found: {pipeline_id}"
                    response.error_code = 2
            else:
                response.success = False
                response.error_message = f"Unknown context request: {request.raw_command}"
                response.error_code = 2

        except Exception as e:
            response.success = False
            response.error_message = f"Context retrieval error: {e}"
            response.error_code = 1

        return response

    def generate_context_id(self) -> str:
        """Generate a unique context ID"""
        import uuid
        return str(uuid.uuid4())

    def cleanup_old_contexts(self):
        """Remove old contexts that exceed retention time"""
        current_time = time.time()
        cutoff_time = current_time - self.context_retention_time

        # Remove old command contexts
        old_command_ids = [
            cmd_id for cmd_id, ctx in self.command_contexts.items()
            if ctx.timestamp < cutoff_time
        ]
        for cmd_id in old_command_ids:
            del self.command_contexts[cmd_id]

        # Remove old pipeline contexts
        old_pipeline_ids = [
            pipe_id for pipe_id, ctx in self.pipeline_contexts.items()
            if ctx.start_time < cutoff_time
        ]
        for pipe_id in old_pipeline_ids:
            del self.pipeline_contexts[pipe_id]

        # Remove old action contexts
        old_action_ids = [
            act_id for act_id, ctx in self.action_contexts.items()
            if (ctx.start_time or ctx.end_time or time.time()) < cutoff_time
        ]
        for act_id in old_action_ids:
            del self.action_contexts[act_id]

        if self.enable_debug:
            self.get_logger().debug(
                f'Cleaned up contexts. Remaining: '
                f'commands={len(self.command_contexts)}, '
                f'pipelines={len(self.pipeline_contexts)}, '
                f'actions={len(self.action_contexts)}'
            )

        # Limit history size
        if len(self.pipeline_contexts) > self.max_context_history:
            # Remove oldest contexts
            sorted_pipelines = sorted(
                self.pipeline_contexts.items(),
                key=lambda x: x[1].start_time
            )
            excess_count = len(sorted_pipelines) - self.max_context_history
            for i in range(excess_count):
                del self.pipeline_contexts[sorted_pipelines[i][0]]

    def get_active_context_summary(self) -> Dict[str, Any]:
        """Get a summary of active contexts"""
        summary = {
            'timestamp': time.time(),
            'active_pipeline_count': len(self.pipeline_contexts),
            'active_command_count': len(self.command_contexts),
            'active_action_count': len(self.action_contexts),
            'current_pipeline_id': self.current_pipeline_id,
            'current_command_id': self.current_command_id,
            'pipeline_summaries': []
        }

        for pipe_id, pipe_ctx in self.pipeline_contexts.items():
            action_statuses = [act.status for act in pipe_ctx.action_contexts]
            summary['pipeline_summaries'].append({
                'pipeline_id': pipe_id,
                'status': pipe_ctx.status,
                'progress': pipe_ctx.progress,
                'action_count': len(pipe_ctx.action_contexts),
                'completed_actions': action_statuses.count('COMPLETED'),
                'failed_actions': action_statuses.count('FAILED'),
                'running_actions': action_statuses.count('RUNNING')
            })

        return summary

    def persist_context(self):
        """Persist current context to file"""
        if not self.enable_persistence:
            return

        try:
            context_data = {
                'command_contexts': {k: asdict(v) for k, v in self.command_contexts.items()},
                'action_contexts': {k: asdict(v) for k, v in self.action_contexts.items()},
                'pipeline_contexts': {k: asdict(v) for k, v in self.pipeline_contexts.items()},
                'current_pipeline_id': self.current_pipeline_id,
                'current_command_id': self.current_command_id,
                'timestamp': time.time()
            }

            with open(self.persistence_file, 'w') as f:
                json.dump(context_data, f, indent=2)

            self.get_logger().info(f'Context persisted to {self.persistence_file}')

        except Exception as e:
            self.get_logger().error(f'Failed to persist context: {e}')

    def load_persisted_context(self):
        """Load persisted context from file"""
        if not self.enable_persistence:
            return

        try:
            with open(self.persistence_file, 'r') as f:
                context_data = json.load(f)

            # Restore command contexts
            self.command_contexts = {
                k: CommandContext(**v) for k, v in context_data.get('command_contexts', {}).items()
            }

            # Restore action contexts
            self.action_contexts = {
                k: ActionContext(**v) for k, v in context_data.get('action_contexts', {}).items()
            }

            # Restore pipeline contexts
            self.pipeline_contexts = {
                k: PipelineContext(
                    pipeline_id=v['pipeline_id'],
                    command_context=CommandContext(**v['command_context']),
                    action_contexts=[ActionContext(**act) for act in v['action_contexts']],
                    start_time=v['start_time'],
                    end_time=v.get('end_time'),
                    status=v['status'],
                    progress=v['progress'],
                    error_message=v.get('error_message', '')
                ) for k, v in context_data.get('pipeline_contexts', {}).items()
            }

            self.current_pipeline_id = context_data.get('current_pipeline_id')
            self.current_command_id = context_data.get('current_command_id')

            self.get_logger().info(f'Context loaded from {self.persistence_file}')

        except FileNotFoundError:
            self.get_logger().info(f'No persisted context found at {self.persistence_file}')
        except Exception as e:
            self.get_logger().error(f'Failed to load persisted context: {e}')

    def reset_context(self):
        """Reset all contexts"""
        self.command_contexts.clear()
        self.action_contexts.clear()
        self.pipeline_contexts.clear()
        self.current_pipeline_id = None
        self.current_command_id = None

        if self.enable_persistence:
            self.persist_context()

        self.get_logger().info('Context reset')


def main(args=None):
    rclpy.init(args=args)
    node = VLAContextManagerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Node interrupted by user')

        # Persist context before shutdown if enabled
        if node.enable_persistence:
            node.persist_context()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()