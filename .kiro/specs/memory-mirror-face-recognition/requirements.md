# Requirements Document

## Introduction

The Memory Mirror is a real-time face recognition prototype designed for live demonstration in a competition. The system uses a laptop's webcam to continuously monitor for faces, identify known individuals from a local database, and provide personalized responses through dynamic UI updates and voice messages. The application serves as an interactive memory aid that recognizes caregivers and family members, displaying their information and playing personalized messages when they approach the mirror.

## Requirements

### Requirement 1

**User Story:** As a competition judge, I want to see a live camera feed from the laptop's webcam, so that I can observe the real-time face detection capabilities of the Memory Mirror system.

#### Acceptance Criteria

1. WHEN the application starts THEN the system SHALL display a live video feed from the laptop's default webcam
2. WHEN the webcam is unavailable THEN the system SHALL display an appropriate error message and gracefully handle the failure
3. WHEN the video feed is active THEN the system SHALL maintain a smooth frame rate suitable for real-time face detection

### Requirement 2

**User Story:** As a user approaching the Memory Mirror, I want my face to be detected and recognized in real-time, so that the system can provide personalized responses without delay.

#### Acceptance Criteria

1. WHEN a face appears in the camera feed THEN the system SHALL detect the face within 2 seconds
2. WHEN a detected face matches a known person in the database THEN the system SHALL identify the person within 3 seconds
3. WHEN multiple faces are present THEN the system SHALL process all visible faces and identify each one independently
4. WHEN face detection is running THEN the system SHALL continuously analyze the video feed without manual intervention

### Requirement 3

**User Story:** As a system administrator, I want to manage known faces through a local folder structure, so that I can easily add, remove, or update person profiles without modifying code.

#### Acceptance Criteria

1. WHEN the system initializes THEN the system SHALL read face data from a "known_faces/" directory structure
2. WHEN a person's folder exists in known_faces/ THEN the system SHALL load all image files from that person's subdirectory for training
3. WHEN the caregiver_data.json file exists THEN the system SHALL load metadata including names, relationships, and voice message content
4. IF a person's folder contains multiple images THEN the system SHALL use all images to improve recognition accuracy
5. WHEN new images are added to a person's folder THEN the system SHALL incorporate them on the next application restart

### Requirement 4

**User Story:** As a user being recognized by the Memory Mirror, I want to see my photo, name, and relationship displayed on the screen, so that I know the system has successfully identified me.

#### Acceptance Criteria

1. WHEN a known person is recognized THEN the system SHALL display their photo within 1 second
2. WHEN a known person is recognized THEN the system SHALL display their name prominently on the UI
3. WHEN a known person is recognized THEN the system SHALL display their relationship information from the metadata
4. WHEN the person moves out of frame THEN the system SHALL return to the neutral state within 2 seconds
5. WHEN recognition confidence is low THEN the system SHALL still display the information but may indicate uncertainty

### Requirement 5

**User Story:** As a user being recognized by the Memory Mirror, I want to hear my personalized voice message, so that I receive a warm, customized greeting that enhances the interactive experience.

#### Acceptance Criteria

1. WHEN a known person is recognized THEN the system SHALL play their personalized voice message automatically
2. WHEN a voice message is playing THEN the system SHALL not interrupt it with new messages for the same person
3. WHEN the same person is recognized again after 30 seconds THEN the system SHALL replay their voice message
4. IF no personalized message exists for a person THEN the system SHALL play a default greeting message
5. WHEN audio playback fails THEN the system SHALL continue to display visual information without audio

### Requirement 6

**User Story:** As a user approaching the Memory Mirror when no one is recognized, I want to see a neutral "Ready to recognize..." state, so that I understand the system is active and waiting for recognition.

#### Acceptance Criteria

1. WHEN no face is detected in the camera feed THEN the system SHALL display "Ready to recognize..." message
2. WHEN a face is detected but not recognized THEN the system SHALL display "Unknown person detected" message
3. WHEN the system is in neutral state THEN the system SHALL continue monitoring for faces without user intervention
4. WHEN transitioning between states THEN the system SHALL provide smooth visual transitions without flickering

### Requirement 7

**User Story:** As a competition demonstrator, I want the Streamlit application to provide a professional and responsive user interface, so that the demonstration appears polished and technically impressive.

#### Acceptance Criteria

1. WHEN the application loads THEN the system SHALL display a clean, professional interface within 5 seconds
2. WHEN face recognition occurs THEN the system SHALL update the UI elements smoothly without page refreshes
3. WHEN displaying person information THEN the system SHALL use appropriate layout and typography for readability
4. WHEN running continuously THEN the system SHALL maintain stable performance without memory leaks or crashes
5. WHEN errors occur THEN the system SHALL display user-friendly error messages without exposing technical details

### Requirement 8

**User Story:** As a user from different cultural backgrounds, I want the Memory Mirror to support multiple languages for both text display and voice messages, so that I can interact with the system in my preferred language.

#### Acceptance Criteria

1. WHEN a person is recognized THEN the system SHALL display their name and relationship information in their preferred language
2. WHEN voice messages are played THEN the system SHALL use the person's preferred language for text-to-speech generation
3. WHEN the system is in neutral state THEN the system SHALL display "Ready to recognize..." message in the default system language
4. WHEN language preferences are stored in caregiver_data.json THEN the system SHALL respect individual language settings per person
5. IF no language preference is specified for a person THEN the system SHALL use the default system language
6. WHEN switching between recognized persons with different language preferences THEN the system SHALL update the UI language accordingly

### Requirement 9

**User Story:** As a developer, I want the system to handle edge cases gracefully, so that the demonstration remains stable and professional even when unexpected situations occur.

#### Acceptance Criteria

1. WHEN the webcam is blocked or covered THEN the system SHALL detect the issue and display an appropriate message
2. WHEN lighting conditions are poor THEN the system SHALL attempt face detection but gracefully handle failures
3. WHEN the known_faces directory is empty THEN the system SHALL start in recognition mode but display appropriate messaging
4. WHEN the caregiver_data.json file is missing or corrupted THEN the system SHALL use default values and log the issue
5. WHEN system resources are limited THEN the system SHALL maintain core functionality while potentially reducing frame rate or recognition frequency