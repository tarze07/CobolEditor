       IDENTIFICATION DIVISION.
       PROGRAM-ID. HELLO-WORLD.
       AUTHOR. CLAUDE CODE.
       DATE-WRITTEN. 2025-11-02.
      *****************************************************************
      * This is a sample COBOL program demonstrating                 *
      * syntax highlighting in the COBOL Editor                      *
      *****************************************************************

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
       SOURCE-COMPUTER. IBM-PC.
       OBJECT-COMPUTER. IBM-PC.

       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT CUSTOMER-FILE ASSIGN TO "CUSTOMERS.DAT"
               ORGANIZATION IS LINE SEQUENTIAL
               ACCESS MODE IS SEQUENTIAL
               FILE STATUS IS WS-FILE-STATUS.

       DATA DIVISION.
       FILE SECTION.
       FD  CUSTOMER-FILE.
       01  CUSTOMER-RECORD.
           05  CUST-ID            PIC 9(5).
           05  CUST-NAME          PIC X(30).
           05  CUST-BALANCE       PIC 9(7)V99.
           05  CUST-CREDIT-LIMIT  PIC 9(7)V99.

       WORKING-STORAGE SECTION.
       01  WS-FILE-STATUS         PIC XX.
           88  WS-FILE-OK         VALUE '00'.
           88  WS-FILE-EOF        VALUE '10'.

       01  WS-CUSTOMER-COUNT      PIC 9(5) VALUE ZERO.
       01  WS-TOTAL-BALANCE       PIC 9(9)V99 VALUE ZERO.
       01  WS-AVERAGE-BALANCE     PIC 9(7)V99 VALUE ZERO.

       01  WS-DISPLAY-LINE.
           05  FILLER             PIC X(15) VALUE 'Customer ID: '.
           05  WS-DISP-ID         PIC 9(5).
           05  FILLER             PIC X(10) VALUE ' Name: '.
           05  WS-DISP-NAME       PIC X(30).
           05  FILLER             PIC X(12) VALUE ' Balance: $'.
           05  WS-DISP-BALANCE    PIC ZZ,ZZZ,ZZ9.99.

       PROCEDURE DIVISION.
       MAIN-PROCEDURE.
      *    Display program header
           DISPLAY "========================================".
           DISPLAY "    CUSTOMER BALANCE REPORT            ".
           DISPLAY "========================================".
           DISPLAY " ".

      *    Open the customer file
           OPEN INPUT CUSTOMER-FILE.

           IF NOT WS-FILE-OK
               DISPLAY "ERROR: Cannot open customer file"
               DISPLAY "File Status: " WS-FILE-STATUS
               STOP RUN
           END-IF.

      *    Process all customer records
           PERFORM READ-CUSTOMER
           PERFORM UNTIL WS-FILE-EOF
               PERFORM PROCESS-CUSTOMER
               PERFORM READ-CUSTOMER
           END-PERFORM.

      *    Display summary
           PERFORM DISPLAY-SUMMARY.

      *    Close file and exit
           CLOSE CUSTOMER-FILE.
           DISPLAY " ".
           DISPLAY "Program completed successfully.".
           STOP RUN.

       READ-CUSTOMER.
           READ CUSTOMER-FILE
               AT END SET WS-FILE-EOF TO TRUE
           END-READ.

       PROCESS-CUSTOMER.
           ADD 1 TO WS-CUSTOMER-COUNT.
           ADD CUST-BALANCE TO WS-TOTAL-BALANCE.

      *    Display customer details
           MOVE CUST-ID TO WS-DISP-ID.
           MOVE CUST-NAME TO WS-DISP-NAME.
           MOVE CUST-BALANCE TO WS-DISP-BALANCE.
           DISPLAY WS-DISPLAY-LINE.

      *    Check if customer is over credit limit
           IF CUST-BALANCE > CUST-CREDIT-LIMIT
               DISPLAY "   *** WARNING: Over credit limit! ***"
           END-IF.

       DISPLAY-SUMMARY.
           DISPLAY " ".
           DISPLAY "========================================".
           DISPLAY "           SUMMARY                     ".
           DISPLAY "========================================".
           DISPLAY "Total Customers: " WS-CUSTOMER-COUNT.
           DISPLAY "Total Balance: $" WS-TOTAL-BALANCE.

           IF WS-CUSTOMER-COUNT > ZERO
               DIVIDE WS-TOTAL-BALANCE BY WS-CUSTOMER-COUNT
                   GIVING WS-AVERAGE-BALANCE ROUNDED
               DISPLAY "Average Balance: $" WS-AVERAGE-BALANCE
           ELSE
               DISPLAY "No customers found in file"
           END-IF.

           DISPLAY "========================================".

       END PROGRAM HELLO-WORLD.
