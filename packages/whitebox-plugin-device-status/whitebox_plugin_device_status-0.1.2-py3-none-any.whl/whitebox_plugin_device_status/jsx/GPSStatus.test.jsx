import { act, render, screen, cleanup } from "@testing-library/react";
import { GPSStatus } from "./GPSStatus";

afterEach(cleanup);

describe("GPSStatus Component", () => {
  let messageHandler;

  beforeAll(() => {
    // Mock Whitebox.sockets
    window.Whitebox = {
      sockets: {
        addEventListener: vi.fn((channel, type, handler) => {
          if (channel === "flight" && type === "message") {
            messageHandler = handler;
          }
        }),
        removeEventListener: vi.fn(),
      },
    };
  });

  it("renders without crashing", () => {
    render(<GPSStatus />);
    expect(screen.getByText("GPS - Not communicating")).toBeInTheDocument();
  });

  it("displays GPS connection status", () => {
    render(<GPSStatus />);
    expect(screen.getByText("GPS - Not communicating")).toBeInTheDocument();

    act(() => {
      // Simulate receiving a message
      messageHandler({
        data: JSON.stringify({
          type: "status_update",
          GPS_connected: true,
          GPS_solution: "3D GPS + SBAS",
          GPS_position_accuracy: 5.0,
        }),
      });
    });

    expect(screen.getByText("GPS - 3D GPS + SBAS, 5.00m")).toBeInTheDocument();
  });

  it("updates GPS status on new messages", () => {
    render(<GPSStatus />);

    act(() => {
      // First message
      messageHandler({
        data: JSON.stringify({
          type: "status_update",
          GPS_connected: true,
          GPS_solution: "3D GPS + SBAS",
          GPS_position_accuracy: 5.0,
        }),
      });
    });

    expect(screen.getByText("GPS - 3D GPS + SBAS, 5.00m")).toBeInTheDocument();

    act(() => {
      // Second message with different data
      messageHandler({
        data: JSON.stringify({
          type: "status_update",
          GPS_connected: true,
          GPS_solution: "2D GPS",
          GPS_position_accuracy: 10.0,
        }),
      });
    });

    expect(screen.getByText("GPS - 2D GPS, 10.00m")).toBeInTheDocument();
  });

  it("handles GPS disconnection", () => {
    render(<GPSStatus />);

    act(() => {
      // Simulate GPS disconnection
      messageHandler({
        data: JSON.stringify({
          type: "status_update",
          GPS_connected: false,
          GPS_solution: "Not communicating",
          GPS_position_accuracy: 0.0,
        }),
      });
    });

    expect(screen.getByText("GPS - Not communicating")).toBeInTheDocument();
  });
});
