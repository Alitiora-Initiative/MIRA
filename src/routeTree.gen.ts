/* eslint-disable */
// Manual route tree for MIRA (Phase 1 wallet UI)
import { Route as rootRoute } from "./routes/__root";
import { Route as IndexRoute } from "./routes/index";
import { Route as DashboardRoute } from "./routes/dashboard";

const IndexRouteWithChildren = IndexRoute;
const DashboardRouteWithChildren = DashboardRoute;

export const routeTree = rootRoute.addChildren([
  IndexRouteWithChildren,
  DashboardRouteWithChildren,
]);
