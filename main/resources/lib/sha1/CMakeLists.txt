#############################################################################
#  This file is part of the Stride software. 
#  It is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by 
#  the Free Software Foundation, either version 3 of the License, or any 
#  later version.
#  The software is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License,
#  along with the software. If not, see <http://www.gnu.org/licenses/>.
#  see http://www.gnu.org/licenses/.
#
#  Copyright 2018, Willem L, Kuylen E & Broeckhove J
#############################################################################
#
#  Build sha1.
#
#############################################################################

#============================================================================
# Build SHA1 lib (build only, no install)
#============================================================================
set(SRC
	src/sha1.cpp
)

add_library(sha1 ${SRC})
set_property(TARGET sha1 PROPERTY POSITION_INDEPENDENT_CODE ON)
unset(SRC)

#############################################################################
