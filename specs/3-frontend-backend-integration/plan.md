# Implementation Plan: Frontend → Backend Integration (Chat + Todos)

**Feature**: Frontend → Backend Integration (Chat + Todos)
**Created**: 2026-01-17
**Status**: Draft
**Plan Version**: 1.0

## Overview

This plan outlines the implementation of integration between the ChatKit frontend and the FastAPI backend to enable real-time chat, AI responses, and todo CRUD operations via API endpoints with proper authentication.

## Scope & Boundaries

### In Scope
- API client wrappers for chat and todo endpoints
- Next.js server actions for secure API calls
- Integration of ChatKit messages with backend `/api/ai/process_message` endpoint
- Synchronization of todo list UI with backend API responses
- Authentication checks and redirects using Better Auth
- Error handling and loading states
- Secure data transmission between frontend and backend

### Out of Scope
- Backend service implementation (assumed to be available)
- AI Agent processing logic (assumed to be available)
- Database schema changes (assumed to be available)
- Infrastructure provisioning and deployment (handled separately)

## Architecture & Design

### High-Level Architecture
```
[ChatKit UI] -> [API Client Wrappers] -> [Server Actions] -> [FastAPI Backend]
     |              |                       |                   |
[Real-time Chat] [Secure Calls]       [Authentication]  [AI Processing]
```

### Component Design

1. **API Client Wrappers**: Service layer that abstracts API calls to the backend
2. **Server Actions**: Secure server-side functions for API communication
3. **Chat Integration**: Connection between ChatKit components and backend endpoints
4. **Todo Synchronization**: UI components that sync with backend todo API
5. **Authentication Layer**: Better Auth integration for session management

### Data Flow

1. Chat messages flow from ChatKit UI → API wrapper → server action → backend `/api/ai/process_message`
2. Todo operations flow from UI → API wrapper → server action → backend `/api/v1/todos`
3. Authentication state flows from Better Auth → server actions → API calls
4. Responses flow back through the same layers to update UI state

## Technical Approach

### 1. API Client Wrapper Implementation
- Create centralized API client in `lib/api.ts`
- Implement methods for chat, todo CRUD, and authentication endpoints
- Add proper error handling and request/response transformation

### 2. Server Actions Implementation
- Create server action functions in `actions/` directory
- Implement secure API calls using server-side authentication
- Add proper error handling and validation

### 3. Chat Integration
- Connect ChatKit message components to `/api/ai/process_message` endpoint
- Implement proper message serialization and deserialization
- Add loading states and error handling for chat operations

### 4. Todo Synchronization
- Connect todo list UI to `/api/v1/todos` endpoints
- Implement real-time synchronization between chat and todo UI
- Add optimistic updates for better UX

### 5. Authentication Integration
- Implement Better Auth client-side session handling
- Add authentication checks to API calls
- Implement proper redirect logic for unauthorized access

### 6. Error Handling & State Management
- Implement comprehensive error handling for network failures
- Add loading states for all API operations
- Implement retry logic for failed requests

## Key Decisions & Rationale

| Decision | Options Considered | Chosen Option | Rationale |
|----------|-------------------|---------------|-----------|
| API Communication | Direct fetch, axios, API client wrappers | API client wrappers | Provides abstraction and centralized error handling |
| Server Communication | Client-side only, server actions, server components | Server actions | Secure server-side execution with Next.js 14 capabilities |
| Authentication | JWT tokens, OAuth, Better Auth | Better Auth | Built-in session management and security features |
| State Management | Global state, local component state, SWR | Mix of local and SWR | Balance between simplicity and performance |

## API Contract

### Chat Endpoint
```
POST /api/ai/process_message
Content-Type: application/json

{
  "message": "Natural language message from user",
  "user_id": "ID of the user",
  "conversation_id": "Optional conversation identifier"
}
```

### Todo Endpoints
```
GET /api/v1/todos
Authorization: Bearer <JWT_TOKEN>
Response: { "data": [Todo], "message": "..." }

POST /api/v1/todos
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
{ "title": "...", "description": "...", "completed": false }
Response: { "data": Todo, "message": "..." }

PUT /api/v1/todos/{id}
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
{ "title": "...", "description": "...", "completed": true }
Response: { "data": Todo, "message": "..." }

DELETE /api/v1/todos/{id}
Authorization: Bearer <JWT_TOKEN>
Response: { "data": null, "message": "..." }
```

## Implementation Phases

### Phase 1: API Client Foundation (Week 1)
- [ ] Create API client wrappers in `lib/api.ts`
- [ ] Implement basic chat and todo endpoint calls
- [ ] Add error handling and request/response transformation
- [ ] Set up authentication headers

### Phase 2: Server Actions (Week 1)
- [ ] Create server action files for todo operations
- [ ] Implement secure server-side API calls
- [ ] Add authentication validation in server actions
- [ ] Set up form actions for todo creation/updating

### Phase 3: Chat Integration (Week 2)
- [ ] Connect ChatKit components to chat endpoint
- [ ] Implement message sending/receiving functionality
- [ ] Add loading and error states for chat operations
- [ ] Test AI response handling

### Phase 4: Todo Synchronization (Week 2)
- [ ] Connect todo list UI to backend API
- [ ] Implement CRUD operations with proper state management
- [ ] Add real-time sync between chat and todo UI
- [ ] Test optimistic updates

### Phase 5: Authentication & Security (Week 3)
- [ ] Implement Better Auth integration
- [ ] Add authentication checks to all API calls
- [ ] Implement proper redirect logic
- [ ] Add session management

### Phase 6: Testing & Optimization (Week 3)
- [ ] Write unit tests for API clients and server actions
- [ ] Perform integration testing
- [ ] Optimize performance and fix bugs
- [ ] Conduct security review

## Dependencies & External Services

- Next.js 14: Framework with App Router and Server Actions
- Better Auth: Authentication and session management
- FastAPI: Backend framework with existing endpoints
- OpenAI Chat Components: Chat UI components (or custom implementation)
- SWR/react-query: Client-side data fetching and caching

## Risk Analysis

| Risk | Impact | Probability | Mitigation Strategy |
|------|---------|-------------|-------------------|
| Backend endpoint availability | High | Low | Verify endpoints exist before implementation |
| Authentication token security | High | Medium | Use secure storage and transmission |
| Chat response latency | Medium | Medium | Implement loading states and caching |
| Cross-site request forgery | High | Low | Implement proper CSRF protection |
| Data synchronization issues | Medium | Medium | Implement proper state management and conflict resolution |

## Success Criteria

### Technical Metrics
- API calls complete within 2 seconds (95th percentile)
- Server actions properly validate authentication
- Client-side state remains consistent with server state
- Error handling provides user-friendly messages

### Functional Metrics
- All user stories from spec successfully implemented
- Chat messages properly transmitted to/from backend
- Todo operations work consistently across interfaces
- Authentication properly enforced on all protected operations
- Loading states provide appropriate feedback to users