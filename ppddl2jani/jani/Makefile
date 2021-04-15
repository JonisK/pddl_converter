
BITWIDTH = -m64

CXXFLAGS =
CXXFLAGS += -g
CXXFLAGS += $(BITWIDTH)
CXXFLAGS += -std=c++11 -Wall -Wextra -pedantic -Wno-deprecated -Werror
CXXFLAGS += -DNDEBUG -fomit-frame-pointer

LDFLAGS =
LDFLAGS += $(BITWIDTH)
LDFLAGS += -g
LDFLAGS += -static -static-libgcc

SRC = $(wildcard *.cc)
OBS = $(patsubst %.cc,%.o,$(SRC))

TARGET = sas2jani

%.o: %.cc
	$(CXX) $(CXXFLAGS) -c $<

$(TARGET): $(OBS)
	$(CXX) -o $(TARGET) $(OBS) $(LDFLAGS)

clean:
	rm -f *.o

distclean: clean
	rm -f $(TARGET)
