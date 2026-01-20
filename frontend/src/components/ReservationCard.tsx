import { Calendar, Clock, MapPin, X, AlertCircle, CheckCircle } from "lucide-react";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { Reservation, Resource, TimeSlot } from "@/api/client";
import { format } from "date-fns";
import { bg } from "date-fns/locale";

interface ReservationCardProps {
  reservation: Reservation;
  resource?: Resource;
  timeSlot?: TimeSlot;
  onCancel?: (reservationId: number) => void;
  isLoading?: boolean;
}

export function ReservationCard({
  reservation,
  resource,
  timeSlot,
  onCancel,
  isLoading = false,
}: ReservationCardProps) {
  const isActive = reservation.status === "Active";
  const startTime = timeSlot ? new Date(timeSlot.start_time) : null;
  const endTime = timeSlot ? new Date(timeSlot.end_time) : null;

  return (
    <Card
      className={cn(
        "group relative overflow-hidden transition-all duration-300 hover:shadow-lg",
        !isActive && "opacity-70"
      )}
      style={{
        borderLeftWidth: "4px",
        borderLeftColor: resource?.color_code || "hsl(var(--primary))",
      }}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg truncate text-card-foreground">
              {resource?.name || `Ресурс #${reservation.resource_id}`}
            </h3>
            <Badge
              variant={isActive ? "default" : "secondary"}
              className={cn(
                "mt-1",
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "bg-muted text-muted-foreground"
              )}
            >
              {isActive ? (
                <>
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Активна
                </>
              ) : (
                <>
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Отменена
                </>
              )}
            </Badge>
          </div>
          {resource && (
            <Badge variant="outline" className="shrink-0">
              {resource.type === "Room" ? "Зала" : "Уред"}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-2 pb-3">
        {startTime && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4 text-primary" />
            <span>
              {format(startTime, "EEEE, d MMMM yyyy", { locale: bg })}
            </span>
          </div>
        )}
        {startTime && endTime && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4 text-primary" />
            <span>
              {format(startTime, "HH:mm")} - {format(endTime, "HH:mm")}
              {timeSlot && (
                <span className="text-muted-foreground/70 ml-1">
                  ({timeSlot.duration_minutes} мин)
                </span>
              )}
            </span>
          </div>
        )}
        {reservation.notes && (
          <p className="text-sm text-muted-foreground mt-2 italic">
            "{reservation.notes}"
          </p>
        )}
      </CardContent>

      {isActive && onCancel && (
        <CardFooter className="pt-0">
          <Button
            variant="destructive"
            size="sm"
            className="w-full gap-2"
            onClick={() => onCancel(reservation.id)}
            disabled={isLoading}
          >
            <X className="h-4 w-4" />
            {isLoading ? "Отменяне..." : "Отмени резервация"}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
