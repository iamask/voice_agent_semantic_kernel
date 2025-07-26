#!/usr/bin/env python3
"""
Test script to verify voice agent setup
"""

import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import pyaudio
        print("✓ PyAudio imported successfully")
    except ImportError as e:
        print(f"✗ PyAudio import failed: {e}")
        return False
    
    try:
        from semantic_kernel.connectors.ai.open_ai import (
            OpenAIChatCompletion,
            OpenAIAudioToText,
            OpenAITextToAudio,
        )
        print("✓ Semantic Kernel OpenAI connectors imported successfully")
    except ImportError as e:
        print(f"✗ Semantic Kernel import failed: {e}")
        return False
    
    return True

def test_audio_devices():
    """Test audio device availability"""
    print("\nTesting audio devices...")
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        input_devices = []
        output_devices = []
        
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
            if device_info['maxOutputChannels'] > 0:
                output_devices.append(device_info['name'])
        
        print(f"✓ Found {len(input_devices)} input device(s):")
        for device in input_devices:
            print(f"  - {device}")
        
        print(f"✓ Found {len(output_devices)} output device(s):")
        for device in output_devices:
            print(f"  - {device}")
        
        p.terminate()
        return True
        
    except Exception as e:
        print(f"✗ Audio device test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\nTesting environment variables...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✓ OPENAI_API_KEY is set")
        return True
    else:
        print("✗ OPENAI_API_KEY is not set")
        print("  Set it with: export OPENAI_API_KEY='your-key-here'")
        return False

def main():
    """Run all tests"""
    print("Voice Agent Setup Test")
    print("=" * 30)
    
    # Test Python version
    print(f"Testing Python version...")
    if sys.version_info >= (3, 10):
        print(f"✓ Python {sys.version.split()[0]} is compatible")
    else:
        print(f"✗ Python {sys.version.split()[0]} is not compatible (need 3.10+)")
        return False
    
    # Run all tests
    tests = [
        test_imports,
        test_audio_devices,
        test_environment
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'=' * 30}")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Your setup is ready.")
        print("\nTo run the voice agent:")
        print("python voice_agent.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()
