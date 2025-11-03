using System;

namespace HelloWorld
{
    class Program
    {
        static void Main(string[] args)
        {
            // This is a comment
            string message = "Hello, World!";
            int number = 42;
            Console.WriteLine(message);

            for (int i = 0; i < 10; i++)
            {
                if (i % 2 == 0)
                {
                    Console.WriteLine($"Even: {i}");
                }
            }
        }
    }
}
