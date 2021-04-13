/* header file to define functions in io.c.  Not named io.h
   because that name is already taken by a system header on 
   Windows */

#ifndef _STD_TESTCASE_IO_H
#define _STD_TESTCASE_IO_H

#include "std_testcase.h" /* needed for the twoint struct */

#ifdef __cplusplus
extern "C" {
#endif

void printLine(const char * line);

void printWLine(const wchar_t * line);

void printIntLine (int intNumber);

void printShortLine (short shortNumber);

void printFloatLine (float floatNumber);

void printLongLine(long longNumber);

void printLongLongLine(int64_t longLongIntNumber);

void printSizeTLine(size_t sizeTNumber);

void printHexCharLine(char charHex);

void printWcharLine(wchar_t wideChar);

void printUnsignedLine(unsigned unsignedNumber);

void printHexUnsignedCharLine(unsigned char unsignedCharacter);

void printDoubleLine(double doubleNumber);

void printStructLine(const twoIntsStruct * structTwoIntsStruct);

void printBytesLine(const unsigned char * bytes, size_t numBytes);

size_t decodeHexChars(unsigned char * bytes, size_t numBytes, const char * hex);

size_t decodeHexWChars(unsigned char * bytes, size_t numBytes, const wchar_t * hex);

int globalReturnsTrue();

int globalReturnsFalse();

int globalReturnsTrueOrFalse();

/* Define some global variables that will get argc and argv */
extern int globalArgc;
extern char** globalArgv;

#ifdef __cplusplus
}
#endif

#endif
