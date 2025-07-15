import styles from "../styles/TopPage.module.css";

type NumberInputTypeMenuProps = {
  label: string;
  state: number;
  setState: React.Dispatch<React.SetStateAction<number>>;
};

export default function NumberInputTypeMenu(props: NumberInputTypeMenuProps) {
  const { label, state, setState } = props;
  return (
    <div className={styles.formGroup}>
      <label>{label}</label>
      <input
        type="number"
        value={state}
        onChange={(e) => setState(Number(e.target.value))}
      />
    </div>
  );
}
