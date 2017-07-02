from .test_session_recorder import TestSessionRecorder

def main():
    TestSessionRecorder().cmdloop(
            TestSessionRecorder.print_header('Test Session Recorder', True))

if __name__ == '__main__': main()
