from focus_bot import FocusBot

def main():
    print("Welcome to Beluga Focus Timer!")
    print("Type 'help' to see available commands")
    print("==================================")
    
    bot = FocusBot()
    
    while True:
        try:
            command = input("\nEnter command: ").strip()
            
            if command.lower() == 'exit':
                print("Thank you for using Beluga Focus Timer! Goodbye!")
                break
            
            response = bot.process_command(command)
            print("\n" + response)
            
        except KeyboardInterrupt:
            print("\nExiting Focus Timer Bot... Goodbye!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == '__main__':
    main()