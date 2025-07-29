import { test } from "@tests/setup";
import { expect } from "@playwright/test";

test.describe("GPS Status Component", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");

    // Small sleep to ensure the everything is fully loaded
    await page.waitForTimeout(1000);
  });

  test("should display disconnected GPS status initially", async ({ page }) => {
    const gpsStatusContainer = page.locator(
      '.c_device_connection:has-text("GPS -")'
    );
    await expect(gpsStatusContainer).toBeVisible();
    await expect(gpsStatusContainer).toContainText("GPS - Not communicating");
    await expect(gpsStatusContainer).toContainText("Disconnected");
  });

  test("should update GPS status when receiving status_update message", async ({
    page,
  }) => {
    // Initial check for disconnected GPS status
    const gpsStatusContainer = page.locator(
      '.c_device_connection:has-text("GPS -")'
    );
    await expect(gpsStatusContainer).toBeVisible();
    await expect(gpsStatusContainer).toContainText("GPS - Not communicating");
    await expect(gpsStatusContainer).toContainText("Disconnected");

    // Send GPS status update via WebSocket
    await page.evaluate(() => {
      const message = {
        type: "status_update",
        GPS_connected: true,
        GPS_solution: "3D GPS + SBAS",
        GPS_position_accuracy: 7.02282,
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that the GPS status has been updated
    await expect(gpsStatusContainer).toContainText(
      "GPS - 3D GPS + SBAS, 7.02m"
    );
    await expect(gpsStatusContainer).toContainText("Connected");
  });

  test("should show disconnected state when GPS loses connection", async ({
    page,
  }) => {
    // First, establish GPS connection
    await page.evaluate(() => {
      const message = {
        type: "status_update",
        GPS_connected: true,
        GPS_solution: "3D GPS + SBAS",
        GPS_position_accuracy: 7.02282,
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that the GPS status is connected
    const gpsStatusContainer = page.locator(
      '.c_device_connection:has-text("GPS -")'
    );
    await expect(gpsStatusContainer).toContainText(
      "GPS - 3D GPS + SBAS, 7.02m"
    );
    await expect(gpsStatusContainer).toContainText("Connected");

    // Now simulate GPS disconnection
    await page.evaluate(() => {
      const message = {
        type: "status_update",
        GPS_connected: false,
        GPS_solution: "Not communicating",
        GPS_position_accuracy: 0,
      };

      const event = new MessageEvent("message", {
        data: JSON.stringify(message),
      });
      const flightSocket = Whitebox.sockets.getSocket("flight", false);
      flightSocket.dispatchEvent(event);
    });

    // Check that the GPS status has been updated to disconnected
    await expect(gpsStatusContainer).toContainText("GPS - Not communicating");
    await expect(gpsStatusContainer).toContainText("Disconnected");
  });
});
