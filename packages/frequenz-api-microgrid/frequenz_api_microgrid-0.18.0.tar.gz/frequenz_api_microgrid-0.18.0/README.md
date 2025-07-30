# Frequenz Microgrid API

[![Build Status](https://github.com/frequenz-floss/frequenz-api-microgrid/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-api-microgrid/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-api-microgrid)](https://pypi.org/project/frequenz-api-microgrid/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-api-microgrid/)

## Introduction

The Frequenz Microgrid API is an service for operating and monitoring electrical
components and sensors within a microgrid. It offers various functionalities
related to microgrid management, including metadata retrieval, component
listing, setting power levels, and controlling the state of components. The API
is structured around the concept of a microgrid, which is a localized energy
system composed of various interconnected components and auxiliary sensors.
Microgrids are typically connected to the main grid, but can also operate
independently, in which case they are referred to as _islanded_ microgrids.

The API supports different _categories_ of electrical components and sensors.
The list of supported electrical component categories cam be found [here](https://github.com/frequenz-floss/frequenz-api-common/blob/v0.4.0/proto/frequenz/api/common/v1/components.proto#L13-L72).
The list of supported sensor categories cam be found [here](https://github.com/frequenz-floss/frequenz-api-common/blob/83e96a9cb3fd88db06c47d29be54da435fc648e3/proto/frequenz/api/common/v1/sensors.proto#L13-L38).
Note that each of these categories could have their own _types_, e.g., inverters
could belong to the type "battery" or "PV". This information is stored in the
metadata of each component and sensor, and is exposed by the API.

The API streams data from the microgrid in real-time, allowing users to retrieve
the status and performance of components and sensors. It also allows users to
control the microgrid by setting power levels and controlling the state of
components.

## Objective

The objective of this API is to provide a standardized interface for monitoring
and controlling components and sensors within a microgrid. The API is designed
to be vendor-agnostic, allowing users to interact with components from various
vendors using the same API.

### Key Features

- **Metadata Retrieval:** The API allows users to retrieve metadata about the
  microgrid, providing information about the microgrid's unique identifier (ID)
  and geographical coordinates.

- **Component Listing:** Users can list components in the microgrid, optionally
  filtered by component IDs and categories.

- **Component Graphs:** The API provides a way to list electrical connections
  between components. Connections are represented as pairs of component IDs that
  are directly connected. The connections can be visualized as a directed graph,
  where the nodes are components, the edges are connections between components,
  and the edge direction represents the direction of power flow in Passive Sign
  Convention.

- **Power Level Control:** Users can set the active and reactive power levels of
  components that support it.

- **Component State Control:** For components that support it, the API supports
  starting, stopping, and transitioning components between these and the
  standby states.

- **Bounds Management:** Users can set exclusion and inclusion bounds for
  specific metrics of a component. These bounds define the acceptable and
  unacceptable ranges of metric values. E.g., one could set the inclusion bounds
  for a battery's DC power to be between -100kW and 100 kW, and the exclusion
  bounds to be between -50kW and 50kW. This would allow the battery to operate
  between -100kW and 100kW, but would prevent it from operating between -50kW
  and 50kW.

### Example Use Cases:

This API is designed for use in microgrid management and control systems. It
can be applied in various scenarios, including:

- **Microgrid Monitoring:** Monitoring the status and performance of components
  in a microgrid, allowing operators to ensure efficient energy distribution.

- **Optimizing Energy Storage:** Managing the charge and discharge power of
  storage systems and generators, e.g., batteries, CHPs, etc., to optimize
  energy storage and consumption within the microgrid.

- **Flexibility Management:** Managing the flexibility of components in the
  microgrid, e.g., by controlling the state and power draw of electrical
  components, to ensure that the microgrid can respond to changes in energy
  demand.

- **Performance Enhancements:** Setting exclusion bounds for metrics to enhance
  system performance and prevent extreme values in battery SoCs or power
  output.

### Target Audience:

This API is designed for application developers in the energy sector who focus
on the tasks of optimizing microgrid electricity flows. Its design aims to be as
developer-friendly as possible, requiring no prior knowledge of any specific
hardware implementation.

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).
