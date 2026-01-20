import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Calendar, Plus, Filter, Loader2, CheckCircle } from "lucide-react";
import { format } from "date-fns";
import { bg } from "date-fns/locale";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { useToast } from "@/hooks/use-toast";
import { ReservationCard } from "@/components/ReservationCard";
import { ResourceCard } from "@/components/ResourceCard";
import { TimeSlotPicker } from "@/components/TimeSlotPicker";
import { reservationsApi, resourcesApi, timeslotsApi, type Resource, type TimeSlot } from "@/api/client";
import { useAuth } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";

// No demo user - this route is protected by AuthProvider/RequireAuth

export default function ReservationsPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("active");
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [selectedTimeSlot, setSelectedTimeSlot] = useState<TimeSlot | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());
  const [notes, setNotes] = useState("");

  const auth = useAuth();

  // Fetch reservations
  const { data: reservationsData, isLoading: reservationsLoading } = useQuery({
    queryKey: ["reservations"],
    queryFn: () => reservationsApi.list(),
    retry: false,
  });

  // Fetch resources
  const { data: resourcesData, isLoading: resourcesLoading } = useQuery({
    queryKey: ["resources"],
    queryFn: () => resourcesApi.list(),
    retry: false,
  });

  // Fetch timeslots for selected resource and date
  const { data: timeslotsData, isLoading: timeslotsLoading } = useQuery({
    queryKey: ["timeslots", selectedResource?.id, selectedDate],
    queryFn: () =>
      timeslotsApi.list({
        resource_id: selectedResource?.id,
        date: selectedDate ? format(selectedDate, "yyyy-MM-dd") : undefined,
      }),
    enabled: !!selectedResource && !!selectedDate,
    retry: false,
  });

  // Timeslot generation is manual and only available to admins via resource controls.

  // Create reservation mutation
  const createMutation = useMutation({
    mutationFn: (data: { resource_id: number; timeslot_id: number; notes?: string }) =>
      reservationsApi.create({ ...data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      queryClient.invalidateQueries({ queryKey: ["timeslots"] });
      toast({
        title: "Резервацията е създадена",
        description: "Успешно резервирахте час.",
      });
      setIsDialogOpen(false);
      resetForm();
    },
    onError: (error: Error) => {
      toast({
        title: "Грешка",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Cancel reservation mutation
  const cancelMutation = useMutation({
    mutationFn: (reservationId: number) =>
      reservationsApi.cancel(reservationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reservations"] });
      queryClient.invalidateQueries({ queryKey: ["timeslots"] });
      toast({
        title: "Резервацията е отменена",
        description: "Успешно отменихте резервацията.",
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Грешка",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const reservations = reservationsData?.reservations || [];
  const resources = resourcesData?.resources || [];
  const timeSlots = timeslotsData?.timeslots || [];

  const activeReservations = reservations.filter((r) => r.status === "Active");
  const cancelledReservations = reservations.filter((r) => r.status === "Cancelled");

  const resetForm = () => {
    setSelectedResource(null);
    setSelectedTimeSlot(null);
    setSelectedDate(new Date());
    setNotes("");
  };

  const handleCreateReservation = () => {
    if (!selectedResource || !selectedTimeSlot) return;

    createMutation.mutate({
      resource_id: selectedResource.id,
      timeslot_id: selectedTimeSlot.id,
      notes: notes || undefined,
    });
  };

  const currentStep = !selectedResource ? 1 : !selectedTimeSlot ? 2 : 3;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Резервации</h1>
          <p className="text-muted-foreground">
            Управлявайте вашите резервации и създавайте нови
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={(open) => { setIsDialogOpen(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Нова резервация
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Създаване на резервация</DialogTitle>
              <DialogDescription>
                Изберете ресурс, дата и час за вашата резервация
              </DialogDescription>
            </DialogHeader>

            {/* Steps indicator */}
            <div className="flex items-center gap-2 py-4">
              {[
                { num: 1, label: "Ресурс" },
                { num: 2, label: "Час" },
                { num: 3, label: "Потвърди" },
              ].map((step, i) => (
                <div key={step.num} className="flex items-center gap-2 flex-1">
                  <div
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium transition-colors",
                      currentStep >= step.num
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    {currentStep > step.num ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : (
                      step.num
                    )}
                  </div>
                  <span className="text-sm hidden sm:inline">{step.label}</span>
                  {i < 2 && (
                    <div className="flex-1 h-0.5 bg-muted mx-2" />
                  )}
                </div>
              ))}
            </div>

            {/* Step 1: Select Resource */}
            {!selectedResource && (
              <div className="space-y-4">
                <h3 className="font-medium">Изберете ресурс</h3>
                {resourcesLoading ? (
                  <div className="grid grid-cols-2 gap-4">
                    {Array.from({ length: 4 }).map((_, i) => (
                      <div key={i} className="h-32 rounded-lg bg-muted animate-pulse" />
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {resources.map((resource) => (
                      <ResourceCard
                        key={resource.id}
                        resource={resource}
                        onSelect={setSelectedResource}
                      />
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Step 2: Select Date & Time */}
            {selectedResource && !selectedTimeSlot && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={() => setSelectedResource(null)}>
                    ← Назад
                  </Button>
                  <h3 className="font-medium">
                    Изберете дата и час за {selectedResource.name}
                  </h3>
                </div>

                <div className="flex flex-col lg:flex-row gap-6">
                  {/* Calendar */}
                  <div className="flex-shrink-0">
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button variant="outline" className="w-full justify-start gap-2">
                          <Calendar className="h-4 w-4" />
                          {selectedDate ? format(selectedDate, "PPP", { locale: bg }) : "Изберете дата"}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <CalendarComponent
                          mode="single"
                          selected={selectedDate}
                          onSelect={setSelectedDate}
                          disabled={(date) => date < new Date()}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>

                  {/* Time Slots */}
                  <div className="flex-1">
                    <TimeSlotPicker
                      timeSlots={timeSlots.filter((s) => s.is_available && new Date(s.start_time) > new Date())}
                      selectedSlot={selectedTimeSlot}
                      onSelect={setSelectedTimeSlot}
                      isLoading={timeslotsLoading}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Confirm */}
            {selectedResource && selectedTimeSlot && (
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Button variant="ghost" size="sm" onClick={() => setSelectedTimeSlot(null)}>
                    ← Назад
                  </Button>
                  <h3 className="font-medium">Потвърдете резервацията</h3>
                </div>

                <Card>
                  <CardContent className="pt-6 space-y-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Ресурс:</span>
                        <p className="font-medium">{selectedResource.name}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Тип:</span>
                        <p className="font-medium">
                          {selectedResource.type === "Room" ? "Зала" : "Уред"}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Дата:</span>
                        <p className="font-medium">
                          {format(new Date(selectedTimeSlot.start_time), "d MMMM yyyy", { locale: bg })}
                        </p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Час:</span>
                        <p className="font-medium">
                          {format(new Date(selectedTimeSlot.start_time), "HH:mm")} -{" "}
                          {format(new Date(selectedTimeSlot.end_time), "HH:mm")}
                        </p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="notes">Бележки (незадължително)</Label>
                      <Textarea
                        id="notes"
                        placeholder="Добавете бележки към резервацията..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                      />
                    </div>
                  </CardContent>
                </Card>

                <DialogFooter>
                  <Button
                    onClick={handleCreateReservation}
                    disabled={createMutation.isPending}
                    className="w-full gap-2"
                  >
                    {createMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Създаване...
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        Потвърди резервация
                      </>
                    )}
                  </Button>
                </DialogFooter>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="active" className="gap-2">
            <Calendar className="h-4 w-4" />
            Активни ({activeReservations.length})
          </TabsTrigger>
          <TabsTrigger value="cancelled" className="gap-2">
            <Filter className="h-4 w-4" />
            Отменени ({cancelledReservations.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-6">
          {reservationsLoading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="h-48 rounded-lg bg-muted animate-pulse" />
              ))}
            </div>
          ) : activeReservations.length === 0 ? (
            <Card className="p-12 text-center">
              <Calendar className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-lg font-medium mb-2">Няма активни резервации</h3>
              <p className="text-muted-foreground mb-4">
                Създайте нова резервация, за да започнете
              </p>
              <Button onClick={() => setIsDialogOpen(true)} className="gap-2">
                <Plus className="h-4 w-4" />
                Нова резервация
              </Button>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {activeReservations.map((reservation) => {
                const resource = resources.find((r) => r.id === reservation.resource_id);
                return (
                  <ReservationCard
                    key={reservation.id}
                    reservation={reservation}
                    resource={resource}
                    onCancel={(id) => cancelMutation.mutate(id)}
                    isLoading={cancelMutation.isPending}
                  />
                );
              })}
            </div>
          )}
        </TabsContent>

        <TabsContent value="cancelled" className="mt-6">
          {cancelledReservations.length === 0 ? (
            <Card className="p-12 text-center">
              <Filter className="h-16 w-16 mx-auto text-muted-foreground/30 mb-4" />
              <h3 className="text-lg font-medium mb-2">Няма отменени резервации</h3>
              <p className="text-muted-foreground">
                Тук ще се показват отменените резервации
              </p>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {cancelledReservations.map((reservation) => {
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
        </TabsContent>
      </Tabs>
    </div>
  );
}
