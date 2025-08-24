import MessageBubble from "./MessageBubble";
import LoadingMessage from "./LoadingMessage";
import EmptyState from "./EmptyState";

export default function MessagesArea({
  chats,
  isLoading,
  formatTime,
  setMessage,
}) {
  if (chats.length === 0) {
    return <EmptyState setMessage={setMessage} />;
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="space-y-6 p-4">
        {chats.map((chat) => (
          <MessageBubble key={chat._id} chat={chat} formatTime={formatTime} />
        ))}
        {isLoading && <LoadingMessage />}
      </div>
    </div>
  );
}
