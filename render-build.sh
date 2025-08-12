#!/usr/bin/env bash
set -o errexit  # Exit on error

# Install ffmpeg
apt-get update
apt-get install -y ffmpeg
