#!/usr/bin/env python3
"""
Basic example demonstrating PocketFlow tracing with Langfuse.

This example shows how to use the @trace_flow decorator to automatically
trace a simple PocketFlow workflow.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from pocketflow import Node, Flow
except ImportError:
    print("❌ PocketFlow not installed. Install with: pip install pocketflow")
    print("   Or install with examples support: pip install pocketflow-tracing[examples]")
    exit(1)

from pocketflow_tracing import trace_flow, TracingConfig


class GreetingNode(Node):
    """A simple node that creates a greeting message."""

    def prep(self, shared):
        """Extract the name from shared data."""
        name = shared.get("name", "World")
        return name

    def exec(self, name):
        """Create a greeting message."""
        greeting = f"Hello, {name}!"
        return greeting

    def post(self, shared, prep_res, exec_res):
        """Store the greeting in shared data."""
        shared["greeting"] = exec_res
        return "default"


class UppercaseNode(Node):
    """A node that converts the greeting to uppercase."""

    def prep(self, shared):
        """Get the greeting from shared data."""
        return shared.get("greeting", "")

    def exec(self, greeting):
        """Convert to uppercase."""
        return greeting.upper()

    def post(self, shared, prep_res, exec_res):
        """Store the uppercase greeting."""
        shared["uppercase_greeting"] = exec_res
        return "default"


@trace_flow(flow_name="BasicGreetingFlow")
class BasicGreetingFlow(Flow):
    """A simple flow that creates and processes a greeting."""

    def __init__(self):
        # Create nodes
        greeting_node = GreetingNode()
        uppercase_node = UppercaseNode()

        # Connect nodes
        greeting_node >> uppercase_node

        # Initialize flow
        super().__init__(start=greeting_node)


def main():
    """Run the basic tracing example."""
    print("🚀 Starting PocketFlow Tracing Basic Example")
    print("=" * 50)

    # Create the flow
    flow = BasicGreetingFlow()

    # Prepare shared data
    shared = {"name": "PocketFlow User"}

    print(f"📥 Input: {shared}")

    # Run the flow (this will be automatically traced)
    try:
        result = flow.run(shared)
        print(f"📤 Output: {shared}")
        print(f"🎯 Result: {result}")
        print("✅ Flow completed successfully!")

        # Print the final greeting
        if "uppercase_greeting" in shared:
            print(f"🎉 Final greeting: {shared['uppercase_greeting']}")

    except Exception as e:
        print(f"❌ Flow failed with error: {e}")
        raise

    print("\n📊 Check your Langfuse dashboard to see the trace!")
    langfuse_host = os.getenv("LANGFUSE_HOST", "your-langfuse-host")
    print(f"   Dashboard URL: {langfuse_host}")


if __name__ == "__main__":
    main()
