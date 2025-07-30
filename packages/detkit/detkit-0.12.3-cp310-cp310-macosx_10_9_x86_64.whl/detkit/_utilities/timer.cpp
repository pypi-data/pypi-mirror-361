/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


// =======
// Headers
// =======

#include "./timer.h"

#if defined(WIN32) || defined(_WIN32) || defined(__WIN32) && \
    !defined(__CYGWIN__)
    #include <windows.h>  // LARGE_INTEGER, QueryPerformanceFrequency,
                          // QueryPerformanceCounter
#elif defined(__unix__) || defined(__unix) || \
    (defined(__APPLE__) && defined(__MACH__))
    #include <sys/time.h>  // timeval, gettimeofday
#else
    #error "Unknown compiler"
#endif

#include <cmath>  // NAN
#include <stdexcept>  // std::runtime_error


// ===========
// Constructor
// ===========

/// \brief constructor for \c Timer
///

Timer::Timer():
    start_time(0),
    stop_time(0)
{
}


// ==========
// Destructor
// ==========

/// \brief Destructor for \c Timer
///

Timer::~Timer()
{
}


// =====
// start
// =====

/// \brief Starts the timer.
///

void Timer::start()
{
    this->start_time = Timer::get_wall_time();
}


// ====
// stop
// ====

/// \brief Stops the timer.
///

void Timer::stop()
{
    this->stop_time = Timer::get_wall_time();
}


// =======
// elapsed
// =======

/// \brief Returns the elapsed time in seconds.
///

double Timer::elapsed() const
{
    return this->stop_time - this->start_time;
}


// =============
// get wall time
// =============

/// \brief Returns the wall time since the epoch.
///

double Timer::get_wall_time()
{
    #if defined(WIN32) || defined(_WIN32) || defined(__WIN32) && \
            !defined(__CYGWIN__)

        LARGE_INTEGER time, freq;
        if (!QueryPerformanceFrequency(&freq))
        {
            std::runtime_error("Cannot obtain system's time frequency.");
            return NAN;
        }

        if (!QueryPerformanceCounter(&time))
        {
            std::runtime_error("Cannot obtain elapsed time.");
            return NAN;
        }

        return static_cast<double>(time.QuadPart) / \
               static_cast<double>(freq.QuadPart);

    #elif defined(__unix__) || defined(__unix) || \
        (defined(__APPLE__) && defined(__MACH__))

        struct timeval time;
        if (gettimeofday(&time, NULL))
        {
            std::runtime_error("Cannot obtain elapsed time.");
            return NAN;
        }

        return static_cast<double>(time.tv_sec) + \
               static_cast<double>(time.tv_usec) * 1e-6;

    #else
            #error "Unknown compiler"
    #endif
}
