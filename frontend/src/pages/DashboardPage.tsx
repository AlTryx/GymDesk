import { useQuery } from "@tanstack/react-query";
import { Calendar, Box, ClipboardList, TrendingUp, Dumbbell } from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ReservationCard } from "@/components/ReservationCard";
import { reservationsApi, resourcesApi } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";

// Demo user ID for now
export default function DashboardPage() {
  const auth = useAuth();

  // Fetch user reservations (server returns reservations for authenticated user)
  const { data: reservationsData, isLoading: reservationsLoading } = useQuery({
    queryKey: ["reservations"],
    queryFn: () => reservationsApi.list(),
    retry: false,
  });

  // Fetch resources
  // Fetch resources scoped to authenticated user
  const { data: resourcesData, isLoading: resourcesLoading } = useQuery({
    queryKey: ["resources"],
    queryFn: () => resourcesApi.list(),
    retry: false,
  });

  const reservations = reservationsData?.reservations || [];
  const resources = resourcesData?.resources || [];
  const activeReservations = reservations.filter((r) => r.status === "Active");

  const stats = [
    {
      label: "Активни резервации",
      value: activeReservations.length,
      icon: Calendar,
      color: "text-primary",
      bg: "bg-primary/10",
    },
    {
      label: "Общо резервации",
      value: reservations.length,
      icon: ClipboardList,
      color: "text-accent-foreground",
      bg: "bg-accent",
    },
    {
      label: "Налични ресурси",
      value: resources.length,
      icon: Box,
      color: "text-chart-4",
      bg: "bg-chart-4/10",
    },
    {
      label: "Този месец",
      value: reservations.filter((r) => {
        if (!r.created_at) return false;
        const date = new Date(r.created_at);
        const now = new Date();
        return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
      }).length,
      icon: TrendingUp,
      color: "text-chart-5",
      bg: "bg-chart-5/10",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary to-primary/80 p-8 text-primary-foreground">
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">Добре дошли в GymDesk</h1>
          <p className="text-primary-foreground/80 max-w-xl">
            Управлявайте вашите резервации за фитнес зали, уреди и инструкторски часове на едно място.
          </p>
          <div className="flex gap-3 mt-6">
            <Link to="/reservations">
              <Button variant="secondary" className="gap-2">
                <Calendar className="h-4 w-4" />
                Нова резервация
              </Button>
            </Link>
            <Link to="/resources">
              <Button variant="outline" className="gap-2 bg-primary-foreground/10 border-primary-foreground/20 text-primary-foreground hover:bg-primary-foreground/20">
                <Box className="h-4 w-4" />
                Разгледай ресурси
              </Button>
            </Link>
          </div>
        </div>
        <Dumbbell className="absolute right-8 top-1/2 -translate-y-1/2 h-32 w-32 opacity-10" />
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="relative overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-xl ${stat.bg}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                  <div>
                    {reservationsLoading || resourcesLoading ? (
                      <Skeleton className="h-8 w-12 mb-1" />
                    ) : (
                      <div className="text-2xl font-bold text-card-foreground">{stat.value}</div>
                    )}
                    <div className="text-sm text-muted-foreground">{stat.label}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Reservations */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            Последни резервации
          </CardTitle>
          <Link to="/reservations">
            <Button variant="ghost" size="sm">
              Виж всички
            </Button>
          </Link>
        </CardHeader>
        <CardContent>
          {reservationsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="h-48 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : reservations.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-lg font-medium text-muted-foreground mb-2">
                Няма резервации
              </h3>
              <p className="text-sm text-muted-foreground/70 mb-4">
                Все още нямате направени резервации
              </p>
              <Link to="/reservations">
                <Button className="gap-2">
                  <Calendar className="h-4 w-4" />
                  Направете първата си резервация
                </Button>
              </Link>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {reservations.slice(0, 6).map((reservation) => {
                const resource = resources.find((r) => r.id === reservation.resource_id);
                return (
                  <ReservationCard
                    key={reservation.id}
                    reservation={reservation}
                    resource={resource}
                  />
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
