#!/bin/bash

echo "Hello, World!" >> entrypoint_was_ran.txt
echo "Working directory: $(pwd)" >> entrypoint_was_ran.txt
echo "Entrypoint script: $0" >> entrypoint_was_ran.txt
echo "Entrypoint arguments: $@" >> entrypoint_was_ran.txt
echo "Entrypoint environment variables: $(env)" >> entrypoint_was_ran.txt
echo "Entrypoint exit code: $?" >> entrypoint_was_ran.txt
echo "Entrypoint PID: $$" >> entrypoint_was_ran.txt
echo "Entrypoint user: $(whoami)" >> entrypoint_was_ran.txt
echo "Entrypoint hostname: $(hostname)" >> entrypoint_was_ran.txt
echo "Entrypoint date: $(date)" >> entrypoint_was_ran.txt