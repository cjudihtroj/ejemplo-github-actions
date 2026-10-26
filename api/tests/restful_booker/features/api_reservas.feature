@HU-02 @api
Feature: API de reservas de Restful Booker
  Como integrador del sistema del hotel
  quiero consultar, crear y eliminar reservas por la API
  para conectar otros sistemas con las reservas

  @CP-03
  Scenario: Consultar una reserva existente
    Given que existe una reserva a nombre de "Utec" con precio total 120
    When se consulta la reserva por su identificador
    Then la respuesta tiene el estado 200
    And la respuesta tiene el apellido "Utec" y el precio total 120

  @CP-04
  Scenario: Consultar una reserva que no existe
    When se consulta la reserva con identificador 999999999
    Then la respuesta tiene el estado 404

  @CP-05
  Scenario: Crear una reserva con datos válidos
    When se crea una reserva a nombre de "Utec" con precio total 150
    Then la respuesta tiene el estado 200
    And la respuesta incluye el identificador de la nueva reserva

  @CP-06
  Scenario: Eliminar una reserva sin autenticación
    Given que existe una reserva a nombre de "Utec" con precio total 120
    When se elimina la reserva sin token
    Then la respuesta tiene el estado 403

  @CP-07
  Scenario: Crear una reserva con datos incompletos
    When se crea una reserva solo con el nombre
    Then la respuesta tiene el estado 400

  @CP-08
  Scenario: Crear una reserva con la salida antes que la entrada
    When se crea una reserva con entrada "2026-11-15" y salida "2026-11-10"
    Then la respuesta tiene el estado 400

  @CP-09
  Scenario: Crear una reserva con precio negativo
    When se crea una reserva a nombre de "Utec" con precio total -50
    Then la respuesta tiene el estado 400

  @CP-10
  Scenario: Obtener un token con una clave incorrecta
    When se solicita un token con usuario "admin" y clave "incorrecta"
    Then la respuesta tiene el estado 401
