@HU-03 @web
Feature: Contacto con el hotel
  Como huésped
  quiero enviar un mensaje al hotel
  para resolver mis dudas antes de reservar

  @CP-11
  Scenario: Un huésped envía un mensaje y el administrador lo recibe
    Given que un huésped está en la página principal
    When envía un mensaje de contacto con el asunto "Consulta de disponibilidad"
    Then ve la confirmación de que su mensaje fue recibido
    When el administrador inicia sesión y abre la bandeja de mensajes
    Then ve el mensaje del huésped con su nombre y asunto

  @CP-12
  Scenario: El administrador elimina un mensaje de la bandeja
    Given que un huésped envió un mensaje de contacto
    When el administrador lo elimina de la bandeja
    Then el mensaje ya no aparece en la bandeja
